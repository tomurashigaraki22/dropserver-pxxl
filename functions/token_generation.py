import requests
import json
from flask import request, jsonify
from datetime import datetime, timedelta
from extensions.extensions import get_db_connection

def get_call_token():
    """
    Get an existing valid token from database or generate a new one if needed
    """
    try:
        data = request.get_json()
        channelName = data.get('channelName')

        if not channelName:
            return {
                "success": False,
                "error": "Channel name is required",
                "message": "Channel name is required to generate a token"
            } 
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if there's a valid token for this channel
        cur.execute("""
            SELECT token, expires_at FROM call_tokens 
            WHERE channel_name = %s AND expires_at > NOW() AND is_expired = FALSE 
            ORDER BY created_at DESC LIMIT 1
        """, (channelName,))
        
        result = cur.fetchone()
        
        if result:
            token, expires_at = result
            cur.close()
            conn.close()
            return {
                "success": True,
                "token": token,
                "expires_at": expires_at.isoformat(),
                "message": "Retrieved existing valid token"
            }
        else:
            # No valid token found, generate a new one
            cur.close()
            conn.close()
            return generate_new_token(channelName=channelName)
            
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve token from database"
        }

def generate_new_token(channelName):
    """
    Generate a new token using the external API and save it to database
    """
    try:
        # API endpoint
        url = "http://148.113.201.195:5500/token/getNew"
        
        # Headers
        headers = {
            "Content-Type": "application/json"
        }
        
        # Payload with one week expiry (604800 seconds = 7 days)
        payload = {
            "tokenType": "rtc",
            "channel": channelName,
            "role": "publisher",
            "uid": "0",
            "expire": 604800  # One week in seconds
        }
        
        # Make the API request
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            response_data = response.json()
            token = response_data.get('token')
            
            if token:
                # Calculate expiration date (one week from now)
                expires_at = datetime.now() + timedelta(weeks=1)
                
                # Save to database
                conn = get_db_connection()
                cur = conn.cursor()
                
                # Mark existing tokens for this channel as expired
                cur.execute("""
                    UPDATE call_tokens SET is_expired = TRUE
                    WHERE channel_name = %s
                """, (channelName,))
                
                # Insert new token
                cur.execute("""
                    INSERT INTO call_tokens (token, expires_at, is_expired, channel_name)
                    VALUES (%s, %s, %s, %s)
                """, (token, expires_at, False, channelName))
                
                conn.commit()
                cur.close()
                conn.close()
                
                return {
                    "success": True,
                    "token": token,
                    "expires_at": expires_at.isoformat(),
                    "message": "New token generated and saved successfully",
                    "api_response": response_data
                }
            else:
                return {
                    "success": False,
                    "error": "No token in API response",
                    "message": "API response did not contain a token",
                    "api_response": response_data
                }
        else:
            return {
                "success": False,
                "error": f"API request failed with status {response.status_code}",
                "message": "Failed to generate token from external API",
                "api_response": response.text
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "Request timeout",
            "message": "API request timed out after 30 seconds"
        }
    except requests.exceptions.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Network error occurred while calling API"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Unexpected error occurred while generating token"
        }