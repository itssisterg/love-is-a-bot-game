"""
Love is a Bot Game - Telegram Dating Game Bot
Created by @itssisterg
GitHub: https://github.com/itssisterg
"""
import os
BOT_TOKEN = "7998825655:AAHbc2Pfkl6iqfM4ZI1iv-RmUhhJIGW5SCI"

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

user_sessions = {}

class GameSession:
    def __init__(self):
        self.gender = None
        self.archetype = None
        self.drama_level = None
        self.location = None
        self.personality = None
        self.day = 1
        self.relationship_score = 0
        self.daily_decisions = {}
        self.potential_partners = {
            "girls": ["alice", "bea", "cara", "diana", "eva"],
            "guys": ["tom", "nick", "leo", "sam", "max"]
        }

def calculate_weighted_impact(session, current_day):
    impact = 0
    for past_day in range(1, current_day):
        days_ago = current_day - past_day
        weight = max(0.1, 1 / (days_ago * 2))
        decision_score = session.daily_decisions.get(past_day, 0)
        impact += decision_score * weight
    return impact

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_sessions[user_id] = GameSession()
    keyboard = [
        [InlineKeyboardButton("Play as Girl", callback_data="gender_girl")],
        [InlineKeyboardButton("Play as Guy", callback_data="gender_guy")]
    ]
    await update.message.reply_text("Welcome to Love is a Bot Game!\nChoose your role:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    session = user_sessions.get(user_id)
    data = query.data

    if data.startswith("gender_"):
        session.gender = data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("Romantic", callback_data="archetype_romantic")],
            [InlineKeyboardButton("Rebel", callback_data="archetype_rebel")],
            [InlineKeyboardButton("Goofy", callback_data="archetype_goofy")]
        ]
        await query.edit_message_text("Pick your archetype:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("archetype_"):
        session.archetype = data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("Chill", callback_data="drama_chill")],
            [InlineKeyboardButton("Spicy", callback_data="drama_spicy")],
            [InlineKeyboardButton("Maximum Drama", callback_data="drama_max")]
        ]
        await query.edit_message_text("How dramatic are you feeling?", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("drama_"):
        session.drama_level = data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("Luxury Yacht", callback_data="location_yacht")],
            [InlineKeyboardButton("Deserted Island", callback_data="location_island")],
            [InlineKeyboardButton("Glamping Site", callback_data="location_glamp")]
        ]
        await query.edit_message_text("Pick your show location:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("location_"):
        session.location = data.split("_")[1]
        keyboard = [
            [InlineKeyboardButton("Empathetic & Curious", callback_data="personality_curious")],
            [InlineKeyboardButton("Flirty & Bold", callback_data="personality_flirty")],
            [InlineKeyboardButton("Awkward but Sweet", callback_data="personality_awkward")],
            [InlineKeyboardButton("Cunning & Strategic", callback_data="personality_cunning")]
        ]
        await query.edit_message_text("Choose your personality:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data.startswith("personality_"):
        session.personality = data.split("_")[1]
        await query.edit_message_text(
            f"Awesome! You're a {session.gender} with a {session.archetype} archetype, "
            f"{session.drama_level} drama level, staying at a {session.location}, "
            f"and you're {session.personality.replace('_', ' ')}.\n\n"
            "Day 1 begins now..."
        )
        await begin_day_one(query, session)

    elif data.startswith("day1_"):
        await handle_day1_action(update, context)

    elif data.startswith("day2_"):
        await handle_day2_action(update, context)

    elif data.startswith("day3_"):
        await handle_day3_action(update, context)

    elif data.startswith("day4_"):
        await handle_day4_action(update, context)

    elif data.startswith("day5_"):
        await handle_day5_action(update, context)

    elif data.startswith("final_pick_"):
        await handle_final_pick(update, context)

async def begin_day_one(query, session):
    keyboard = [
        [InlineKeyboardButton("Go on a date", callback_data="day1_date")],
        [InlineKeyboardButton("Stir some drama", callback_data="day1_drama")],
        [InlineKeyboardButton("Explore the location", callback_data="day1_explore")]
    ]
    await query.message.reply_text(
        "🌞 Day 1: You’ve just arrived and everyone’s mingling.\nWhat do you want to do?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_day1_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    session = user_sessions.get(user_id)
    choice = query.data

    scores = {"day1_date": 1, "day1_drama": -1, "day1_explore": 0}
    msgs = {
        "day1_date": "You went on a sweet date! Sparks might be flying... 💕",
        "day1_drama": "You stirred the pot! Drama alert! 🔥",
        "day1_explore": "You explored the grounds and uncovered a secret spot. 🗺️"
    }
    score = scores.get(choice, 0)
    msg = msgs.get(choice, "You did nothing notable.")

    session.daily_decisions[session.day] = score
    weighted_impact = calculate_weighted_impact(session, session.day + 1)

    if weighted_impact > 0.5:
        msg += "\nYour charm is definitely noticed by others!"
    elif weighted_impact < -0.5:
        msg += "\nPeople are wary of your drama-making ways."

    session.relationship_score += score
    session.day += 1

    await query.edit_message_text(f"{msg}")
    await begin_day_two(query, session)

async def begin_day_two(query, session):
    impact = calculate_weighted_impact(session, 2)
    if impact > 0.5:
        intro = "People remember your charm from yesterday. You're off to a great start!"
    elif impact < -0.5:
        intro = "Your drama yesterday has some contestants talking... tread carefully."
    else:
        intro = "The day starts with neutral vibes. What will you do?"

    keyboard = [
        [InlineKeyboardButton("Plan a group activity", callback_data="day2_group")],
        [InlineKeyboardButton("Flirt with a new contestant", callback_data="day2_flirt")],
        [InlineKeyboardButton("Spy on others", callback_data="day2_spy")]
    ]
    await query.message.reply_text(f"🌅 Day 2: {intro}\nChoose your next move:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_day2_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    session = user_sessions.get(user_id)
    choice = query.data

    scores = {"day2_group": 1, "day2_flirt": 1, "day2_spy": -1}
    msgs = {
        "day2_group": "You organized a fun group event! Everyone’s bonding. 🤗",
        "day2_flirt": "You flirted successfully! Chemistry is building. 💘",
        "day2_spy": "You got caught spying! People are suspicious. 👀"
    }
    score = scores.get(choice, 0)
    msg = msgs.get(choice, "You stayed low-key today.")

    session.daily_decisions[session.day] = score
    impact = calculate_weighted_impact(session, session.day + 1)

    if impact > 0.5:
        msg += "\nYour reputation continues to improve!"
    elif impact < -0.5:
        msg += "\nTension is rising around you."

    session.relationship_score += score
    session.day += 1

    await query.edit_message_text(f"{msg}")
    await begin_day_three(query, session)

async def begin_day_three(query, session):
    impact = calculate_weighted_impact(session, 3)
    if impact > 0.5:
        intro = "You’re becoming the star of the show! Everyone’s eyes are on you."
    elif impact < -0.5:
        intro = "Rumors are swirling. Watch your back."
    else:
        intro = "Another day, another chance to make an impression."

    keyboard = [
        [InlineKeyboardButton("Host a talent show", callback_data="day3_talent")],
        [InlineKeyboardButton("Confess a secret", callback_data="day3_secret")],
        [InlineKeyboardButton("Start a rumor", callback_data="day3_rumor")]
    ]
    await query.message.reply_text(f"🌞 Day 3: {intro}\nChoose your action:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_day3_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    session = user_sessions.get(user_id)
    choice = query.data

    scores = {"day3_talent": 1, "day3_secret": 0, "day3_rumor": -1}
    msgs = {
        "day3_talent": "Your talent wowed everyone! Popularity rises. 🌟",
        "day3_secret": "You shared something personal, building trust. 🤫",
        "day3_rumor": "The rumor you started caused drama. Brace yourself. 💥"
    }
    score = scores.get(choice, 0)
    msg = msgs.get(choice, "You kept a low profile today.")

    session.daily_decisions[session.day] = score
    impact = calculate_weighted_impact(session, session.day + 1)

    if impact > 0.5:
        msg += "\nYour influence keeps growing!"
    elif impact < -0.5:
        msg += "\nPeople are cautious around you."

    session.relationship_score += score
    session.day += 1

    await query.edit_message_text(f"{msg}")
    await begin_day_four(query, session)

async def begin_day_four(query, session):
    impact = calculate_weighted_impact(session, 4)
    if impact > 0.5:
        intro = "Your alliances are strong. The game is heating up!"
    elif impact < -0.5:
        intro = "Enemies are making moves against you. Stay alert."
    else:
        intro = "The tension is palpable. How will you play your cards?"

    keyboard = [
        [InlineKeyboardButton("Plan a surprise party", callback_data="day4_party")],
        [InlineKeyboardButton("Confront a rival", callback_data="day4_confront")],
        [InlineKeyboardButton("Take a solo retreat", callback_data="day4_retreat")]
    ]
    await query.message.reply_text(f"🌞 Day 4: {intro}\nChoose your strategy:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_day4_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    session = user_sessions.get(user_id)
    choice = query.data

    scores = {"day4_party": 1, "day4_confront": -1, "day4_retreat": 0}
    msgs = {
        "day4_party": "The surprise party was a hit! Bonds deepen. 🎉",
        "day4_confront": "The confrontation escalated tensions. ⚔️",
        "day4_retreat": "You found peace and clarity alone. 🧘"
    }
    score = scores.get(choice, 0)
    msg = msgs.get(choice, "You stayed quiet and observed.")

    session.daily_decisions[session.day] = score
    impact = calculate_weighted_impact(session, session.day + 1)

    if impact > 0.5:
        msg += "\nYour power in the game is undeniable!"
    elif impact < -0.5:
        msg += "\nYour rivals are plotting carefully."

    session.relationship_score += score
    session.day += 1

    await query.edit_message_text(f"{msg}")
    await begin_day_five(query, session)

async def begin_day_five(query, session):
    impact = calculate_weighted_impact(session, 5)
    if impact > 0.5:
        intro = "Final day! Your popularity is at its peak."
    elif impact < -0.5:
        intro = "Final day! The tension has never been higher."
    else:
        intro = "Final day! Everything comes down to this."

    keyboard = [
        [InlineKeyboardButton("Make a heartfelt speech", callback_data="day5_speech")],
        [InlineKeyboardButton("Reveal a secret crush", callback_data="day5_crush")],
        [InlineKeyboardButton("Throw a last-minute party", callback_data="day5_party")]
    ]
    await query.message.reply_text(f"🌅 Day 5: {intro}\nChoose your final move before picking a partner:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_day5_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    session = user_sessions.get(user_id)
    choice = query.data

    scores = {"day5_speech": 1, "day5_crush": 1, "day5_party": 0}
    msgs = {
        "day5_speech": "Your speech moved everyone deeply. ❤️",
        "day5_crush": "You revealed your crush and hearts fluttered. 💓",
        "day5_party": "The party was wild and unforgettable! 🎊"
    }
    score = scores.get(choice, 0)
    msg = msgs.get(choice, "You prepared quietly for the final choice.")

    session.daily_decisions[session.day] = score
    impact = calculate_weighted_impact(session, session.day + 1)

    if impact > 0.5:
        msg += "\nYour legacy here will not be forgotten!"
    elif impact < -0.5:
        msg += "\nDrama marks your final day."

    session.relationship_score += score
    session.day += 1

    await query.edit_message_text(f"{msg}\n\nNow, it's time to pick your partner!")
    await present_final_pick(query, session)

async def present_final_pick(query, session):
    gender = session.gender
    partners = []
    if gender == "girl":
        partners = session.potential_partners["guys"] + ["Surprise: Pick a girl!"]
    else:
        partners = session.potential_partners["girls"] + ["Surprise: Pick a guy!"]

    keyboard = []
    for p in partners:
        key = p.lower().replace(" ", "_").replace(":", "")
        keyboard.append([InlineKeyboardButton(p.title(), callback_data=f"final_pick_{key}")])

    await query.message.reply_text("Choose your final partner:", reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_final_pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    session = user_sessions.get(user_id)
    pick = query.data[len("final_pick_"):]

    if "surprise" in pick:
        partner_name = "Surprise partner of your own gender!"
        personality = "Bold and unexpected!"
        msg = "You shocked everyone by choosing a surprise partner of your own gender! Bold move! 🎉"
    else:
        partner_name = pick.replace("_", " ").title()
        personality_map = {
            "alice": "Romantic and empathetic",
            "bea": "Spicy and bold",
            "cara": "Goofy and fun",
            "diana": "Cunning and strategic",
            "eva": "Sweet and shy",
            "tom": "Charming and confident",
            "nick": "Mysterious and intense",
            "leo": "Flirty and playful",
            "sam": "Laid-back and cool",
            "max": "Adventurous and daring",
        }
        personality = personality_map.get(pick, "Unique personality")

        msg = f"You chose {partner_name} as your partner! What a romantic ending! 💖"

    # Find top moment (day with highest decision score)
    if session.daily_decisions:
        top_day = max(session.daily_decisions, key=session.daily_decisions.get)
        top_score = session.daily_decisions[top_day]
        moment_msgs = {
            1: "Your sweet date on Day 1 set the tone for the show.",
            2: "The group activity you planned on Day 2 brought everyone closer.",
            3: "Your talent show performance on Day 3 stole the spotlight.",
            4: "The surprise party on Day 4 was unforgettable.",
            5: "Your heartfelt speech on Day 5 touched all hearts.",
        }
        top_moment = moment_msgs.get(top_day, "Many memorable moments throughout the game!")
    else:
        top_moment = "A game full of surprises!"

    summary = (
        f"{msg}\n\n"
        f"✨ *Your Partner's Personality:* {personality}\n"
        f"🌟 *Your Top Moment:* {top_moment}\n\n"
        f"Thanks for playing *Love is a Bot Game*! 🎉\n"
        f"Share the fun with your friends: https://t.me/LoveIsABotGameBot"
    )

    await query.edit_message_text(summary, parse_mode='Markdown')

def main():
    app = ApplicationBuilder().token("BOT_TOKEN").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.run_polling()

if __name__ == '__main__':
    main()
