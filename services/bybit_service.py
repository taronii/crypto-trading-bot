"""Bybit API service for real trading operations"""
from pybit.unified_trading import HTTP
from typing import Dict, List, Optional, Any
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class BybitService:
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """Initialize Bybit service with API credentials"""
        self.testnet = testnet
        self.client = HTTP(
            testnet=testnet,
            api_key=api_key,
            api_secret=api_secret
        )
    
    def test_connection(self) -> Dict[str, Any]:
        """Test API connection and return account info"""
        try:
            logger.info(f"Testing connection with testnet={self.testnet}")
            
            # Get server time to test basic connectivity
            server_time = self.client.get_server_time()
            logger.info(f"Server time response: {server_time}")
            
            # Get account info
            logger.info("Getting wallet balance...")
            account_info = self.client.get_wallet_balance(accountType="UNIFIED")
            logger.info(f"Wallet balance response status: {account_info.get('retCode')}")
            
            if account_info["retCode"] == 0:
                # Extract balance info
                if account_info["result"]["list"]:
                    result = account_info["result"]["list"][0]
                    total_equity = float(result.get("totalEquity", 0))
                    available_balance = float(result.get("totalAvailableBalance", 0))
                    
                    # Get coin balances
                    coin_balances = {}
                    for coin in result.get("coin", []):
                        # Handle empty strings and None values
                        equity = coin.get("equity", "0")
                        available = coin.get("availableToWithdraw", "0") 
                        wallet_balance = coin.get("walletBalance", "0")
                        
                        # Convert to float, handling empty strings
                        coin_balances[coin["coin"]] = {
                            "equity": float(equity) if equity and equity != "" else 0,
                            "available": float(available) if available and available != "" else 0,
                            "wallet_balance": float(wallet_balance) if wallet_balance and wallet_balance != "" else 0
                        }
                    
                    logger.info(f"Parsed balances - Total: {total_equity}, Available: {available_balance}")
                    
                    return {
                        "success": True,
                        "connected": True,
                        "balance": {
                            "total": total_equity,
                            "available": available_balance,
                            "currency": "USDT",
                            "coins": coin_balances
                        },
                        "server_time": server_time["result"]["timeNano"]
                    }
                else:
                    logger.warning("No wallet data found in response")
                    return {
                        "success": False,
                        "connected": False,
                        "error": "No wallet data found"
                    }
            else:
                logger.error(f"API returned error: {account_info.get('retMsg', 'Unknown error')}")
                return {
                    "success": False,
                    "connected": False,
                    "error": account_info.get("retMsg", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"API connection test failed: {str(e)}")
            return {
                "success": False,
                "connected": False,
                "error": str(e)
            }
    
    def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get current positions"""
        try:
            params = {"category": "linear", "settleCoin": "USDT"}
            if symbol:
                params["symbol"] = symbol
            
            response = self.client.get_positions(**params)
            
            if response["retCode"] == 0:
                positions = []
                for pos in response["result"]["list"]:
                    if float(pos["size"]) > 0:  # Only include open positions
                        positions.append({
                            "id": pos.get("positionIdx", f"{pos['symbol']}_{pos['side']}"),  # Use positionIdx or fallback
                            "symbol": pos["symbol"],
                            "side": pos["side"],
                            "size": float(pos["size"]),
                            "entry_price": float(pos["avgPrice"]) if pos["avgPrice"] else 0,
                            "current_price": float(pos["markPrice"]) if pos["markPrice"] else 0,
                            "unrealized_pnl": float(pos["unrealisedPnl"]) if pos["unrealisedPnl"] else 0,
                            "realized_pnl": float(pos.get("realisedPnl", 0)) if pos.get("realisedPnl") else 0,
                            "margin": float(pos["positionIM"]) if pos["positionIM"] else 0,
                            "leverage": int(pos["leverage"]) if pos["leverage"] else 1,
                            "position_status": pos.get("positionStatus", "Normal"),
                            "created_at": datetime.fromtimestamp(int(pos["createdTime"]) / 1000).isoformat() + "Z" if pos.get("createdTime") else datetime.utcnow().isoformat() + "Z",
                            "updated_at": datetime.fromtimestamp(int(pos["updatedTime"]) / 1000).isoformat() + "Z" if pos.get("updatedTime") else datetime.utcnow().isoformat() + "Z"
                        })
                
                return positions
            else:
                logger.error(f"Failed to get positions: {response.get('retMsg', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting positions: {str(e)}")
            return []
    
    def get_balance(self) -> Dict[str, Any]:
        """Get account balance information"""
        try:
            response = self.client.get_wallet_balance(accountType="UNIFIED")
            
            if response["retCode"] == 0:
                balances = {}
                if response["result"]["list"]:
                    account = response["result"]["list"][0]
                    
                    # Extract total account values
                    balances["total_equity"] = float(account.get("totalEquity", 0))
                    balances["available_balance"] = float(account.get("totalAvailableBalance", 0))
                    
                    # Extract coin balances
                    for coin in account.get("coin", []):
                        coin_name = coin["coin"]
                        
                        # Helper function to safely convert to float
                        def safe_float(value, default=0):
                            if value is None or value == "":
                                return default
                            try:
                                return float(value)
                            except (ValueError, TypeError):
                                return default
                        
                        balances[coin_name] = {
                            "equity": safe_float(coin.get("equity")),
                            "available_balance": safe_float(coin.get("equity")),  # Use equity as available balance
                            "wallet_balance": safe_float(coin.get("walletBalance")),
                            "unrealized_pnl": safe_float(coin.get("unrealisedPnl")),
                            "cum_realized_pnl": safe_float(coin.get("cumRealisedPnl"))
                        }
                
                return balances
            else:
                logger.error(f"Failed to get balance: {response.get('retMsg', 'Unknown error')}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting balance: {str(e)}")
            return {}
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker information for a symbol"""
        try:
            response = self.client.get_tickers(
                category="linear",
                symbol=symbol
            )
            
            if response["retCode"] == 0 and response["result"]["list"]:
                ticker = response["result"]["list"][0]
                return {
                    "symbol": ticker["symbol"],
                    "lastPrice": ticker["lastPrice"],
                    "bid1Price": ticker["bid1Price"],
                    "ask1Price": ticker["ask1Price"],
                    "volume24h": ticker["volume24h"],
                    "turnover24h": ticker["turnover24h"],
                    "highPrice24h": ticker["highPrice24h"],
                    "lowPrice24h": ticker["lowPrice24h"],
                    "prevPrice24h": ticker["prevPrice24h"],
                    "price24hPcnt": ticker["price24hPcnt"]
                }
            else:
                logger.error(f"Failed to get ticker: {response.get('retMsg', 'Unknown error')}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting ticker for {symbol}: {str(e)}")
            return {}
    
    def get_orders(self, symbol: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get orders"""
        try:
            params = {"category": "linear", "settleCoin": "USDT"}
            if symbol:
                params["symbol"] = symbol
            if status:
                params["orderStatus"] = status
            
            response = self.client.get_open_orders(**params)
            
            if response["retCode"] == 0:
                orders = []
                for order in response["result"]["list"]:
                    orders.append({
                        "id": order["orderId"],
                        "symbol": order["symbol"],
                        "side": order["side"],
                        "type": order["orderType"],
                        "status": order["orderStatus"],
                        "price": float(order["price"]),
                        "quantity": float(order["qty"]),
                        "filled": float(order["cumExecQty"]),
                        "remaining": float(order["leavesQty"]),
                        "created_at": datetime.fromtimestamp(int(order["createdTime"]) / 1000).isoformat() + "Z",
                        "updated_at": datetime.fromtimestamp(int(order["updatedTime"]) / 1000).isoformat() + "Z"
                    })
                
                return orders
            else:
                logger.error(f"Failed to get orders: {response.get('retMsg', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting orders: {str(e)}")
            return []
    
    def get_trade_history(self, symbol: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get trade history"""
        try:
            params = {
                "category": "linear",
                "limit": limit
            }
            if symbol:
                params["symbol"] = symbol
            
            response = self.client.get_executions(**params)
            
            if response["retCode"] == 0:
                trades = []
                for trade in response["result"]["list"]:
                    trades.append({
                        "id": trade["execId"],
                        "order_id": trade["orderId"],
                        "symbol": trade["symbol"],
                        "side": trade["side"],
                        "price": float(trade["execPrice"]),
                        "quantity": float(trade["execQty"]),
                        "fee": float(trade["execFee"]),
                        "realized_pnl": float(trade.get("closedPnl", 0)),
                        "executed_at": datetime.fromtimestamp(int(trade["execTime"]) / 1000).isoformat() + "Z"
                    })
                
                return trades
            else:
                logger.error(f"Failed to get trade history: {response.get('retMsg', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting trade history: {str(e)}")
            return []
    
    def get_klines(self, symbol: str, interval: str = "60", limit: int = 200) -> List[Dict[str, Any]]:
        """Get kline/candlestick data"""
        try:
            # Convert interval to Bybit format (numeric minutes)
            interval_map = {
                "1m": "1",
                "3m": "3", 
                "5m": "5",
                "15m": "15",
                "30m": "30",
                "1h": "60",
                "2h": "120",
                "4h": "240",
                "6h": "360",
                "12h": "720",
                "1d": "D",
                "1w": "W",
                "1M": "M"
            }
            
            bybit_interval = interval_map.get(interval, interval)
            logger.info(f"Getting klines for {symbol}, interval={bybit_interval}, limit={limit}")
            
            # For spot pairs, use 'spot' category
            category = "spot" if not self.testnet else "linear"
            
            response = self.client.get_kline(
                category=category,
                symbol=symbol,
                interval=bybit_interval,
                limit=limit
            )
            
            logger.info(f"Kline response retCode: {response.get('retCode')}, retMsg: {response.get('retMsg')}")
            
            if response["retCode"] == 0:
                klines = []
                kline_list = response.get("result", {}).get("list", [])
                logger.info(f"Got {len(kline_list)} klines from API")
                
                for kline in kline_list:
                    klines.append({
                        "timestamp": datetime.fromtimestamp(int(kline[0]) / 1000).isoformat() + "Z",
                        "open": float(kline[1]),
                        "high": float(kline[2]),
                        "low": float(kline[3]),
                        "close": float(kline[4]),
                        "volume": float(kline[5])
                    })
                
                # Reverse to get chronological order
                klines.reverse()
                return klines
            else:
                logger.error(f"Failed to get klines: {response.get('retMsg', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting klines: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
    
    def set_leverage(self, symbol: str, leverage: int = 10) -> Dict[str, Any]:
        """Set leverage for a symbol"""
        try:
            response = self.client.set_leverage(
                category="linear",
                symbol=symbol,
                buyLeverage=str(leverage),
                sellLeverage=str(leverage)
            )
            
            if response["retCode"] == 0:
                logger.info(f"Leverage set to {leverage}x for {symbol}")
                return {"success": True, "leverage": leverage}
            else:
                logger.error(f"Failed to set leverage: {response.get('retMsg', 'Unknown error')}")
                return {"success": False, "error": response.get('retMsg')}
                
        except Exception as e:
            logger.error(f"Error setting leverage: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def place_order(self, symbol: str, side: str, qty: float, order_type: str = "Market", 
                   price: Optional[float] = None, stop_loss: Optional[float] = None,
                   take_profit: Optional[float] = None, leverage: int = 10) -> Dict[str, Any]:
        """Place a new order"""
        try:
            # レバレッジを設定（10倍）
            leverage_result = self.set_leverage(symbol, leverage)
            if not leverage_result.get("success"):
                logger.warning(f"Could not set leverage for {symbol}, continuing with current leverage")
            
            params = {
                "category": "linear",
                "symbol": symbol,
                "side": side,
                "orderType": order_type,
                "qty": str(qty),
                "timeInForce": "IOC" if order_type == "Market" else "GTC"
            }
            
            if order_type == "Limit" and price:
                params["price"] = str(price)
            
            if stop_loss:
                params["stopLoss"] = str(stop_loss)
            
            if take_profit:
                params["takeProfit"] = str(take_profit)
            
            response = self.client.place_order(**params)
            
            if response["retCode"] == 0:
                return {
                    "retCode": 0,
                    "success": True,
                    "result": {
                        "orderId": response["result"]["orderId"],
                        "orderLinkId": response["result"]["orderLinkId"]
                    },
                    "order_id": response["result"]["orderId"],
                    "order_link_id": response["result"]["orderLinkId"]
                }
            else:
                return {
                    "retCode": response["retCode"],
                    "success": False,
                    "error": response.get("retMsg", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"Error placing order: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def cancel_order(self, symbol: str, order_id: str) -> Dict[str, Any]:
        """Cancel an order"""
        try:
            response = self.client.cancel_order(
                category="linear",
                symbol=symbol,
                orderId=order_id
            )
            
            if response["retCode"] == 0:
                return {"success": True}
            else:
                return {
                    "success": False,
                    "error": response.get("retMsg", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"Error canceling order: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def close_position(self, symbol: str, qty: Optional[float] = None, position_idx: int = 0) -> Dict[str, Any]:
        """Close a specific position"""
        try:
            # Get current position details
            positions = self.get_positions(symbol=symbol)
            position = next((p for p in positions if p["symbol"] == symbol), None)
            
            if not position:
                return {
                    "success": False,
                    "error": "Position not found"
                }
            
            # Use provided qty for partial close, or position size for full close
            close_qty = qty if qty is not None else position["size"]
            
            # Place a market order in the opposite direction to close the position
            response = self.client.place_order(
                category="linear",
                symbol=symbol,
                side="Sell" if position["side"] == "Buy" else "Buy",
                orderType="Market",
                qty=str(close_qty),
                timeInForce="IOC",
                reduceOnly=True,
                positionIdx=position_idx
            )
            
            if response["retCode"] == 0:
                return {
                    "success": True,
                    "order_id": response["result"]["orderId"]
                }
            else:
                return {
                    "success": False,
                    "error": response.get("retMsg", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"Error closing position: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_account_performance(self, days: int = 30) -> Dict[str, Any]:
        """Calculate account performance metrics"""
        try:
            # Get current balance
            wallet = self.client.get_wallet_balance(accountType="UNIFIED")
            if wallet["retCode"] != 0:
                return {}
            
            current_equity = float(wallet["result"]["list"][0]["totalEquity"])
            
            # Get P&L records (Bybit API limit: max 7 days per request)
            end_time = datetime.utcnow()
            # Limit to 7 days if requested days > 7
            actual_days = min(days, 7)
            start_time = end_time - timedelta(days=actual_days)
            
            # Use closed P&L endpoint for trade history
            pnl_response = self.client.get_closed_pnl(
                category="linear",
                startTime=int(start_time.timestamp() * 1000),
                endTime=int(end_time.timestamp() * 1000),
                limit=200
            )
            
            if pnl_response["retCode"] == 0:
                pnl_list = pnl_response["result"]["list"]
                
                total_pnl = sum(float(p["closedPnl"]) for p in pnl_list)
                winning_trades = [p for p in pnl_list if float(p["closedPnl"]) > 0]
                losing_trades = [p for p in pnl_list if float(p["closedPnl"]) < 0]
                
                win_rate = len(winning_trades) / len(pnl_list) if pnl_list else 0
                avg_win = sum(float(p["closedPnl"]) for p in winning_trades) / len(winning_trades) if winning_trades else 0
                avg_loss = sum(float(p["closedPnl"]) for p in losing_trades) / len(losing_trades) if losing_trades else 0
                
                return {
                    "total_return": total_pnl,
                    "total_return_percent": (total_pnl / current_equity) * 100 if current_equity > 0 else 0,
                    "total_trades": len(pnl_list),
                    "winning_trades": len(winning_trades),
                    "losing_trades": len(losing_trades),
                    "win_rate": win_rate,
                    "avg_win": avg_win,
                    "avg_loss": abs(avg_loss),
                    "profit_factor": (avg_win * len(winning_trades)) / (abs(avg_loss) * len(losing_trades)) if losing_trades and avg_loss != 0 else 0,
                    "current_equity": current_equity
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error calculating performance: {str(e)}")
            return {}

# Singleton instance
_bybit_service: Optional[BybitService] = None

def get_bybit_service(api_key: str, api_secret: str, testnet: bool = True) -> BybitService:
    """Get or create Bybit service instance"""
    global _bybit_service
    
    # Always create a new instance when credentials are provided
    # This ensures the service uses the latest credentials
    if api_key and api_secret:
        _bybit_service = BybitService(api_key, api_secret, testnet)
    elif _bybit_service is None:
        # Create with empty credentials if no service exists
        _bybit_service = BybitService("", "", testnet)
    
    return _bybit_service