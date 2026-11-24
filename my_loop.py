"""Your agent's loop, which you design in step 1a. The homework page says what the
loop is for, under "1a. Design the loop" (also in instructions/part1.md), and the
check tells you each rule it must follow when your loop breaks it.

You design the loop as an outline in plain words, in WRITEUP.md under 1a. The
loop below the line that says where it goes is Claude's translation of that
outline, written with the parts in loop_parts.py: each line of your outline is a
comment, with about one line of Python for it under it. To change the loop,
change your outline and ask Claude to translate it again.

Check it after each translation. The check uses a scripted stand-in for the
model and for Wikipedia, so it needs no key and costs nothing:

    uv run python check_loop.py

Part 0 runs the agent on the reference loop. Once every rule passes, the agent
runs on this loop and no other: the runs of 1c and later need it to pass.
"""

import anthropic

# The names below include every one the file had before the parts, so that a loop written
# then still runs.
from agent import (ACCEPTED, DECLINED, INSTRUCTIONS, MAX_REJECTED, MAX_STEPS, MODEL, NO_ANSWER,
                   OUT_OF_STEPS, RAN_OUT, REJECTED, REJECTED_TOO_OFTEN, REMINDED, REMINDER,
                   TOOLS, answer_problem, clean_answer, finish, run_tool)
from loop_parts import Conversation


def run_agent(claim, client=None, max_steps=MAX_STEPS, lookup=run_tool):
    """Check one claim. Returns what talk.accept() or talk.stop() returns."""
    client = client or anthropic.Anthropic()
    system = INSTRUCTIONS.read_text()
    messages = [{"role": "user", "content": f"Claim: {claim}"}]
    trace, read_so_far = [], []
    talk = Conversation(claim, client, system, messages, trace, read_so_far, lookup)
    steps = 0          # lookups made so far
    rejected = 0       # answers sent back so far

    # Your loop should repeatedly call the model with the message history so far, and ask for
    # its next step. It should check whether the model has given an answer yet. If not, it should
    # make the lookups that step asks for, and add what they return to the history. It should
    # also pay attention to whether the loop has reached its limit: a claim that runs out of
    # lookups cannot be decided.
    # ---- your loop goes below this line (step 1a) ----

    # Set the count of lookups to 0.
    # (steps, set to 0 above, is this count)

    # Ask the model the question, and to pick items, properties, and values worth searching for.
    reply = talk.ask()

    # Store the model's reply.
    stored_reply = reply

    while True:  # the repeat that "go back to 'If the reply gives an answer'" asks for

        # If the reply gives an answer, stop and return that answer and the count of lookups, even if the reply also asks for searches or reads.
        if stored_reply.answer is not None:
            return talk.accept(stored_reply.answer, steps)

        # If the reply asks for any searches or reads:
        if stored_reply.lookups:

            # If the count of lookups has reached its limit, stop with no answer and return the number of lookups.
            if steps >= max_steps:
                return talk.stop(RAN_OUT, steps)

            # Make every search and read that reply asked for.
            found = [talk.run(call) for call in stored_reply.lookups]

            # Add the number of searches and reads that were just made to the count of lookups.
            steps += len(stored_reply.lookups)

            # Store what came back from all of them.
            for call, result in zip(stored_reply.lookups, found):
                talk.give(call, result)

            # Give the model everything that came back, all together, and ask it again.
            talk.send_results()
            reply = talk.ask()

            # Store the model's new reply and go back to "If the reply gives an answer".
            stored_reply = reply
            continue

        # If the reply has neither an answer nor any searches or reads:
        if stored_reply.answer is None and not stored_reply.lookups:

            # Remind the model to answer the question, and ask it again.
            talk.remind()
            reply = talk.ask()

            # Store the model's new reply and go back to "If the reply gives an answer".
            stored_reply = reply
            continue
