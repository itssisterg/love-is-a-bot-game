"""
Love is a Bot Game - Telegram Dating Game Bot
Created by @itssisterg
GitHub: https://github.com/itssisterg
"""

import os
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes


user_sessions = {}
all_final_picks = {}  # Store everyone's final picks (user_id or cast_member name as keys)
cast_members = ["alice", "bea", "cara", "diana", "eva", "tom", "nick", "leo", "sam", "max"]


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
        self.interaction_in_progress = False
        self.interaction_partner = None
        self.interaction_step = 0
        self.potential_partners = {
            "girls": ["alice", "bea", "cara", "diana", "eva"],
            "guys": ["tom", "nick", "leo", "sam", "max"]
        }
        self.final_pick = None


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


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_sessions:
        del user_sessions[user_id]  # Clear session
    keyboard = [
        [InlineKeyboardButton("Play as Girl", callback_data="gender_girl")],
        [InlineKeyboardButton("Play as Guy", callback_data="gender_guy")]
    ]
    await update.message.reply_text(
        "Game restarted! Welcome back to Love is a Bot Game!\nChoose your role:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    session = user_sessions.get(user_id)
    data = query.data

    if session is None and not data.startswith("gender_"):
        await query.edit_message_text("Please start a new game with /start or /restart.")
        return

    # If interaction is in progress, handle interaction choices only
    if session and session.interaction_in_progress:
        await handle_interaction_button(update, context)
        return

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

    elif data.startswith("interact_"):
        # Player chose a partner to interact with
        partner_key = data[len("interact_"):]
        await start_interaction(query, session, partner_key)


async def begin_day_one(query, session):
    keyboard = [
        [InlineKeyboardButton("Go on a date", callback_data="day1_date")],
        [InlineKeyboardButton("Stir some drama", callback_data="day1_drama")],
        [InlineKeyboardButton("Explore the location", callback_data="day1_explore")]
    ]
    await query.message.reply_text(
        f"🌞 Day 1: You’ve just arrived and everyone’s mingling.\nWhat do you want to do?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def handle_day_action(update: Update, context: ContextTypes.DEFAULT_TYPE, day_prefix, scores, msgs, next_day_func):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    session = user_sessions.get(user_id)
    choice = query.data

    score = scores.get(choice, 0)
    msg = msgs.get(choice, "You did nothing notable.")

    session.daily_decisions[session.day] = score
    weighted_impact = calculate_weighted_impact(session, session.day + 1)

    if weighted_impact > 0.5:
        msg += "\nYour charm is definitely noticed by others!"
    elif weighted_impact < -0.5:
        msg += "\nPeople are wary of your drama-making ways."

    session.relationship_score += score
    day_msg = f"Day {session.day} update:\n{msg}"  # Add day header here

    # Instead of progressing day here, wait for interaction phase next
    # Show daily update then prompt to pick partner to interact with
    await query.edit_message_text(day_msg)
    await prompt_interaction(query, session)


async def handle_day1_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    scores = {"day1_date": 1, "day1_drama": -1, "day1_explore": 0}
    msgs = {
        "day1_date": "You went on a sweet date! Sparks might be flying... 💕",
        "day1_drama": "You stirred the pot! Drama alert! 🔥",
        "day1_explore": "You explored the grounds and uncovered a secret spot. 🗺️"
    }
    await handle_day_action(update, context, "day1", scores, msgs, begin_day_two)


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
    scores = {"day2_group": 1, "day2_flirt": 1, "day2_spy": -1}
    msgs = {
        "day2_group": "You organized a fun group event! Everyone’s bonding. 🤗",
        "day2_flirt": "You flirted successfully! Chemistry is building. 💘",
        "day2_spy": "You got caught spying! People are suspicious. 👀"
    }
    await handle_day_action(update, context, "day2", scores, msgs, begin_day_three)


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
    scores = {"day3_talent": 1, "day3_secret": 0, "day3_rumor": -1}
    msgs = {
        "day3_talent": "Your talent wowed everyone! Popularity rises. 🌟",
        "day3_secret": "You shared something personal, building trust. 🤫",
        "day3_rumor": "The rumor you started caused drama. Brace yourself. 💥"
    }
    await handle_day_action(update, context, "day3", scores, msgs, begin_day_four)


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
    scores = {"day4_party": 1, "day4_confront": -1, "day4_retreat": 0}
    msgs = {
        "day4_party": "The surprise party was a hit! Bonds deepen. 🎉",
        "day4_confront": "The confrontation escalated tensions. ⚔️",
        "day4_retreat": "You found peace and clarity alone. 🧘"
    }
    await handle_day_action(update, context, "day4", scores, msgs, begin_day_five)


async def begin_day_five(query, session):
    # Day 5: NO interactions, only final pick
    await query.message.reply_text(
        "Day 5: No more chatting.\nTime to pick your final partner!",
    )
    await present_final_pick(query, session)


async def handle_day5_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # No actions handled on day 5 other than final pick
    pass


async def prompt_interaction(query, session):
    # After daily choice (days 1-4), prompt user to pick a partner to interact with
    gender = session.gender
    partners = []
    if gender == "girl":
        partners = session.potential_partners["guys"]
    else:
        partners = session.potential_partners["girls"]

    keyboard = []
    for p in partners:
        keyboard.append([InlineKeyboardButton(p.title(), callback_data=f"interact_{p}")])

    await query.message.reply_text(
        f"Day {session.day}: Who would you like to interact with for 5 minutes? Your choice affects your relationship.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def start_interaction(query, session, partner_key):
    session.interaction_in_progress = True
    session.interaction_partner = partner_key
    session.interaction_step = 1

    await query.edit_message_text(
        f"Starting 5-minute interaction with {partner_key.title()}.\n\n"
        "Q1: They ask — What’s your idea of a perfect date?\n"
        "Choose your response:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Something adventurous!", callback_data="interaction_1_adventure")],
            [InlineKeyboardButton("Cozy and quiet night in.", callback_data="interaction_1_cozy")],
            [InlineKeyboardButton("A big party with friends!", callback_data="interaction_1_party")]
        ])
    )


async def handle_interaction_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    session = user_sessions.get(user_id)
    data = query.data

    if not data.startswith("interaction_"):
        await query.edit_message_text("Invalid interaction response.")
        session.interaction_in_progress = False
        return

    step = session.interaction_step

    if step == 1:
        mapping = {
            "interaction_1_adventure": 1,
            "interaction_1_cozy": 2,
            "interaction_1_party": 0
        }
        choice_score = mapping.get(data, 0)
        session.relationship_score += choice_score

        session.interaction_step = 2
        await query.edit_message_text(
            f"Q2: {session.interaction_partner.title()} asks — What do you value most in a partner?\nChoose:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Loyalty", callback_data="interaction_2_loyalty")],
                [InlineKeyboardButton("Humor", callback_data="interaction_2_humor")],
                [InlineKeyboardButton("Ambition", callback_data="interaction_2_ambition")]
            ])
        )
    elif step == 2:
        mapping = {
            "interaction_2_loyalty": 2,
            "interaction_2_humor": 1,
            "interaction_2_ambition": 0
        }
        choice_score = mapping.get(data, 0)
        session.relationship_score += choice_score

        session.interaction_step = 3
        await query.edit_message_text(
            f"Q3: {session.interaction_partner.title()} wonders — How do you handle conflict?\nChoose:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Talk it out calmly", callback_data="interaction_3_calm")],
                [InlineKeyboardButton("Take time alone then discuss", callback_data="interaction_3_alone")],
                [InlineKeyboardButton("Avoid it and hope it passes", callback_data="interaction_3_avoid")]
            ])
        )
    elif step == 3:
        mapping = {
            "interaction_3_calm": 2,
            "interaction_3_alone": 1,
            "interaction_3_avoid": -1
        }
        choice_score = mapping.get(data, 0)
        session.relationship_score += choice_score

        session.interaction_in_progress = False
        session.interaction_partner = None
        session.interaction_step = 0

        day = session.day
        session.day += 1  # advance day after interaction

        await query.edit_message_text(
            f"Interaction complete! Your relationship score changed by {choice_score}.\n"
            f"Current total relationship score: {session.relationship_score}\n\n"
            f"Day {day} interaction ended."
        )

        # Start next day or final pick
        if day == 1:
            await begin_day_two(query, session)
        elif day == 2:
            await begin_day_three(query, session)
        elif day == 3:
            await begin_day_four(query, session)
        elif day == 4:
            await begin_day_five(query, session)
        elif day >= 5:
            await present_final_pick(query, session)


async def present_final_pick(query, session):
    gender = session.gender
    partners = session.potential_partners["guys"] if gender == "girl" else session.potential_partners["girls"]
    keyboard = []
    for p in partners:
        key = p.lower().replace(" ", "_")
        keyboard.append([InlineKeyboardButton(p.title(), callback_data=f"final_pick_{key}")])
    await query.message.reply_text("Choose your final partner:", reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_final_pick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    session = user_sessions.get(user_id)
    pick = query.data[len("final_pick_"):]
    session.final_pick = pick

    # Save user pick in global dict
    all_final_picks[user_id] = pick

    # Autogenerate picks for cast members (simulate their choices) if not already done
    for cast_member in cast_members:
        if cast_member not in all_final_picks:
            # Cast member picks random choice from all users (only this user for now) + cast members excluding self
            choices_pool = [user_id] + [c for c in cast_members if c != cast_member]
            all_final_picks[cast_member] = random.choice(choices_pool)

    # Check if user picked a cast member
    if pick in cast_members:
        partner_pick = all_final_picks.get(pick)
        is_match = (partner_pick == user_id)  # mutual pick = match
    else:
        # No matching for surprise or invalid picks, treat as no match
        is_match = False

    partner_name = pick.title().replace("_", " ")

    if is_match:
        result_msg = f"🎉 Congratulations! {partner_name} also picked YOU! It's a MATCH! 💞"
    else:
        result_msg = f"😢 You picked {partner_name}, but they chose someone else. No match this time."

    await query.edit_message_text(
        f"{result_msg}\n\n"
        f"Your final relationship score: {session.relationship_score}\n"
        f"Thanks for playing Love is a Bot Game! Share this with friends. Use /restart to play again."
    )


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO)
    TOKEN = "7998825655:AAHbc2Pfkl6iqfM4ZI1iv-RmUhhJIGW5SCI"
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("restart", restart))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot is starting...")
    app.run_polling()
