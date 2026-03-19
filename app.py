import requests
import random
from flask import Flask, jsonify

app = Flask(__name__)

# ==========================================
# 🎨 CUSTOM 48px LED EFFECTS 
# ==========================================

def get_bouncing_ball_promo():
    """Injects a high-res bouncing basketball GIF."""
    # Using a GIPHY link that allows hotlinking to ensure it shows up on the board
    ball_gif = "<img src='https://i.giphy.com/3o7TKpxpUuU0v77-vS.gif' height='40' style='vertical-align: middle;' />"
    return f"{ball_gif} WELCOME TO THE VENTURE COURTSIDE CLUB - ENJOY MARCH MADNESS! {ball_gif}"

def get_sponsor_ad(sponsor_name="TOLEDO ATHLETICS"):
    """Hijacks the ticker background with Toledo Midnight Blue and Gold text."""
    return f"<span style='background-color:#00205B; color:#FFD100; font-weight:bold; padding:0 30px;'> 👑 TONIGHT'S MADNESS IS BROUGHT TO YOU BY {sponsor_name} 👑 </span>"

def get_kernel_panic_glitch(hype_message):
    """Simulates a system crash before revealing a major game alert."""
    crash_header = "<span style='color:red; font-weight:bold;'> 🛑 FATAL_EXCEPTION: 0x000000F4 [OVERFLOW] </span>"
    glitch_chars = "01!<>-_\\/[]{}—=+*^?#XFA9"
    garbage_data = "".join(random.choice(glitch_chars) for _ in range(45))
    recovery = "<span style='color:#00FF00;'> >> REBOOTING... >> OVERRIDE ACCEPTED >> </span>"
    payload = f"<span style='background-color:red; color:white; font-weight:bold; padding:0 15px;'> 🚨 {hype_message} 🚨 </span>"
    return f"{crash_header}{garbage_data}{recovery}{payload}"

# ==========================================
# 🏀 LIVE DATA & DIRECTOR ENGINE
# ==========================================

@app.route('/rise-ticker-feed', methods=['GET'])
def get_ticker_feed():
    url = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        games_data = data.get('events', [])
    except Exception as e:
        return jsonify({"tickerName": "VCC Hype Feed", "items": [{"text": "⚠️ VCC TICKER: Establishing satellite uplink..."}]})

    messages = []
    active_games = [g for g in games_data if g['status']['type']['state'] == 'in']
    
    if not active_games:
        messages.append("📺 WAITING FOR NEXT TIP-OFF | GRAB A DRINK! 🍻")
    else:
        for idx, game in enumerate(active_games[:4]):
            competitors = game['competitions'][0]['competitors']
            home_team = next(c for c in competitors if c['homeAway'] == 'home')
            away_team = next(c for c in competitors if c['homeAway'] == 'away')
            
            home_name = home_team['team']['abbreviation']
            away_name = away_team['team']['abbreviation']
            home_pts = int(home_team.get('score', 0))
            away_pts = int(away_team.get('score', 0))
            
            clock = game['status']['displayClock']
            period = game['status']['period']
            time_str = f"{clock} {period}H" if period <= 2 else f"{clock} OT"
            
            diff = abs(home_pts - away_pts)
            matchup = f"{away_name} vs {home_name}"
            
            if diff <= 5 and period >= 2:
                raw_alert = f"CLUTCH ALERT: {matchup} | {diff} PT GAME ({away_pts}-{home_pts}) | {time_str}"
                messages.append(get_kernel_panic_glitch(raw_alert))
            elif diff >= 15:
                messages.append(f"📺 {matchup} | BLOWOUT ({away_pts}-{home_pts}) | {time_str}")
            else:
                messages.append(f"📺 {matchup} | {away_pts}-{home_pts} | {time_str}")

    # Final Assembly
    messages.insert(0, get_bouncing_ball_promo())
    messages.append(get_sponsor_ad("TOLEDO ATHLETICS"))

    return jsonify({
        "tickerName": "VCC Hype Feed",
        "items": [{"text": msg} for msg in messages]
    })

# ==========================================
# 📡 THE TICKER XML/RSS TRANSLATOR
# ==========================================

@app.route('/rise-rss-feed', methods=['GET'])
def get_rss_feed():
    # Fetch the live JSON data from our main route
    json_response = get_ticker_feed().get_json()
    rss_items = ""
    
    for item in json_response['items']:
        # CDATA ensures the Rise App renders the HTML tags instead of printing them
        rss_items += f"<item><title><![CDATA[{item['text']}]]></title></item>"
    
    xml_output = f"""<?xml version="1.0" encoding="UTF-8" ?>
    <rss version="2.0">
    <channel>
        <title>VCC Hype Feed</title>
        <description>Live March Madness Hype for VCC</description>
        {rss_items}
    </channel>
    </rss>"""
    
    return xml_output, 200, {'Content-Type': 'application/xml'}

if __name__ == '__main__':
    # Using Replit/Cloud compatible port
    app.run(host='0.0.0.0', port=8080)
