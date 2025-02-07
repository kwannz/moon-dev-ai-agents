from src.agents.base_agent import BaseAgent
from src.models import model_factory
from src.data.helius_client import HeliusClient

class MyStrategy(BaseAgent):
    def __init__(self):
        super().__init__(agent_type="strategy")
        self.name = "Lumix Custom Strategy ✨"
        self.model = model_factory.get_model("ollama", "deepseek-r1:1.5b")
        self.helius_client = HeliusClient()
        
    def analyze_market(self, token_address: str) -> dict:
        try:
            # Get token data
            df = self.helius_client.get_token_data(token_address)
            if df.empty:
                return {"action": "HOLD", "reason": "No data available"}
            
            # Basic strategy logic
            current_price = float(df['Close'].iloc[-1])
            ma20 = float(df['MA20'].iloc[-1]) if 'MA20' in df.columns else current_price
            
            if current_price > ma20 * 1.05:  # 5% above MA20
                return {"action": "BUY", "reason": "Price above MA20"}
            elif current_price < ma20 * 0.95:  # 5% below MA20
                return {"action": "SELL", "reason": "Price below MA20"}
            
            return {"action": "HOLD", "reason": "Price within MA20 range"}
            
        except Exception as e:
            print(f"Error in strategy analysis: {str(e)}")
            return {"action": "HOLD", "reason": "Analysis error"}
