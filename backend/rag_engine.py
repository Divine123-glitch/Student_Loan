"""
NELFUND Agentic RAG Engine
Uses LangGraph for intelligent document retrieval and response generation
"""

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# State Type for LangGraph
class AgentState(TypedDict):
    messages: List
    query: str
    needs_retrieval: bool
    retrieved_docs: List[str]
    response: str
    sources: List[str]


class NELFUNDRAGAgent:
    """
    Agentic RAG system with conditional retrieval and conversation memory
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the RAG agent
        
        Args:
            persist_directory: Path to ChromaDB vector store
        """
        self.persist_directory = persist_directory
        
        # Initialize LLM
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found in .env file. "
                "Please add it: OPENAI_API_KEY=sk-your-key-here"
            )
        
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.3,
            openai_api_key=api_key
        )
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=api_key
        )
        
        # Load vector store
        self.vectorstore = self._load_vectorstore()
        
        # Build LangGraph workflow
        self.graph = self._build_graph()
    
    def _load_vectorstore(self) -> Chroma:
        """
        Load the vector store from disk
        
        Returns:
            Chroma vector store instance
        """
        if not os.path.exists(self.persist_directory):
            print(f"Warning: Vector store not found at {self.persist_directory}")
            print("Please run the setup script to create the vector store:")
            print("   python vector_store.py")
            raise FileNotFoundError(
                f"Vector store not found. Run setup first."
            )
        
        vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings,
            collection_name="nelfund_docs"
        )
        
        print(f"✓ Vector store loaded from {self.persist_directory}")
        return vectorstore
    
    def _classify_query(self, state: AgentState) -> AgentState:
        """
        Classify if query needs document retrieval
        
        This is the "agentic" part - deciding when to retrieve
        """
        query = state["query"].lower().strip()
        
        # Greetings and simple queries don't need retrieval
        no_retrieval_patterns = [
            "hello", "hi", "hey", "good morning", "good afternoon", 
            "good evening", "thanks", "thank you", "bye", "goodbye",
            "how are you", "what's up", "what can you do"
        ]
        
        # Check if query is just a greeting
        if any(pattern in query for pattern in no_retrieval_patterns):
            state["needs_retrieval"] = False
        else:
            # For substantive questions, retrieve documents
            state["needs_retrieval"] = True
        
        return state
    
    def _retrieve_documents(self, state: AgentState) -> AgentState:
        """
        Retrieve relevant documents from vector store
        """
        if not state["needs_retrieval"]:
            return state
        
        query = state["query"]
        
        # Retrieve top 4 most relevant chunks with scores
        results = self.vectorstore.similarity_search_with_score(query, k=4)
        
        # Extract content and sources
        state["retrieved_docs"] = [doc.page_content for doc, score in results]
        
        # Extract unique sources from metadata
        sources = []
        for doc, score in results:
            source = doc.metadata.get("source", "Unknown Document")
            # Extract just the filename
            if "/" in source or "\\" in source:
                source = os.path.basename(source)
            if source not in sources:
                sources.append(source)
        
        state["sources"] = sources
        
        return state
    
    def _generate_response(self, state: AgentState) -> AgentState:
        """
        Generate response using LLM
        """
        query = state["query"]
        messages = state.get("messages", [])
        
        if state["needs_retrieval"]:
            # RAG response with retrieved context
            context = "\n\n".join(state["retrieved_docs"])
            
            system_prompt = """You are a helpful AI assistant for NELFUND (Nigerian Education Loan Fund).

Your role is to help Nigerian students understand:
- Eligibility requirements for student loans
- Application process and required documentation
- Repayment terms and conditions
- Covered institutions and courses
- Any other NELFUND-related queries

IMPORTANT RULES:
1. ONLY use information from the provided context below
2. If the answer isn't in the context, say "I don't have that specific information in the NELFUND documents I have access to. I recommend visiting the official NELFUND website at nelfund.gov.ng for the most current information."
3. Be clear, friendly, and encouraging to students
4. Always cite your sources when providing information
5. Break down complex information into simple, easy-to-understand terms
6. Use Nigerian context and examples when helpful

Context from NELFUND documents:
{context}

Remember: Your goal is to empower Nigerian students with accurate information about accessing higher education funding."""

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{query}")
            ])
            
            # Convert message history to proper format
            chat_history = []
            for msg in messages[-6:]:  # Last 3 exchanges (6 messages)
                if msg.get("role") == "user":
                    chat_history.append(HumanMessage(content=msg["content"]))
                elif msg.get("role") == "assistant":
                    chat_history.append(AIMessage(content=msg["content"]))
            
            # Generate response
            chain = prompt | self.llm
            response = chain.invoke({
                "context": context,
                "chat_history": chat_history,
                "query": query
            })
            
            state["response"] = response.content
            
        else:
            # Simple response without retrieval
            system_prompt = """You are a friendly AI assistant for NELFUND (Nigerian Education Loan Fund).

For greetings and simple interactions:
- Respond warmly and professionally
- Offer to help with NELFUND-related questions
- Be encouraging and supportive to students
- Keep responses brief and friendly"""

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{query}")
            ])
            
            chain = prompt | self.llm
            response = chain.invoke({"query": query})
            
            state["response"] = response.content
            state["sources"] = []
        
        return state
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow
        
        Flow: Classify → Retrieve (conditional) → Generate
        """
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify", self._classify_query)
        workflow.add_node("retrieve", self._retrieve_documents)
        workflow.add_node("generate", self._generate_response)
        
        # Define edges
        workflow.set_entry_point("classify")
        workflow.add_edge("classify", "retrieve")
        workflow.add_edge("retrieve", "generate")
        workflow.add_edge("generate", END)
        
        return workflow.compile()
    
    def query(self, user_query: str, chat_history: Optional[List[dict]] = None) -> dict:
        """
        Main query method - process user question through the agent
        
        Args:
            user_query: User's question
            chat_history: Previous conversation messages
            
        Returns:
            Dictionary with response, sources, and metadata
        """
        # Initialize state
        initial_state = {
            "messages": chat_history or [],
            "query": user_query,
            "needs_retrieval": True,
            "retrieved_docs": [],
            "response": "",
            "sources": []
        }
        
        # Run through LangGraph workflow
        result = self.graph.invoke(initial_state)
        
        return {
            "response": result["response"],
            "sources": result["sources"],
            "needs_retrieval": result["needs_retrieval"]
        }


# Singleton instance
_agent_instance: Optional[NELFUNDRAGAgent] = None


def get_rag_agent() -> NELFUNDRAGAgent:
    """
    Get or create the RAG agent singleton
    
    Returns:
        NELFUNDRAGAgent instance
    """
    global _agent_instance
    
    if _agent_instance is None:
        print("Initializing NELFUND RAG Agent...")
        _agent_instance = NELFUNDRAGAgent()
        print("✓ RAG Agent ready!")
    
    return _agent_instance


def test_agent():
    """
    Test the RAG agent with sample queries
    """
    print("\n" + "="*80)
    print("TESTING NELFUND RAG AGENT")
    print("="*80 + "\n")
    
    agent = get_rag_agent()
    
    test_queries = [
        "Hello!",
        "Am I eligible for NELFUND student loan?",
        "What documents do I need to apply?",
        "When do I start repaying the loan?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test {i} ---")
        print(f"Query: {query}")
        print(f"{'─'*80}")
        
        result = agent.query(query)
        
        print(f"Response: {result['response']}")
        
        if result['sources']:
            print(f"\nSources:")
            for source in result['sources']:
                print(f"  • {source}")
        
        print(f"\nNeeded Retrieval: {result['needs_retrieval']}")
        print("\n" + "="*80)
        
        if i < len(test_queries):
            input("\nPress Enter for next test...")


if __name__ == "__main__":
    test_agent()