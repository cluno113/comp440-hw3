# COMP 440 HW3 write-up

Name: Claire Kuno

Type each answer after the `>` under its question. An answer can run over several lines, but a blank line
ends it: to start a new paragraph, put a line with just `>` between the two. In a table, fill every cell   
of every numbered row. Claude may paste a program's output where a question asks for it, but never an
answer. The homework page ticks a step when every answer in its section is filled in.

## Learning goals

In this homework you will:

- Understand what makes a program an *agent*. You will study a language model that picks the next Wikipedia search query, reads the page that comes back, and decides when to stop.
- Gain hands-on experience with the loop around the model by writing it yourself: its tools, its instructions, and its limit of 12 lookups.
- Compare the agent with two simpler methods on your claims, and measure how effective each one is.
- Check the agent's evidence yourself, and decide whether accuracy alone is a fair measure of it.

For extra credit, in Part 3, you find out why the agent fails on your claims, make one change, and see where Wikipedia, which is written by its volunteer editors, is thin, out of date or wrong.

# Part 0: Set up and check one claim

## 0a. Get your copy running

There is nothing to write for this step except your name, after `Name:` at the top of this file.

## 0b. Ask the model to assess a claim without tools

What verdict did the model give (*supported*, *refuted* or *doesn't say*), and what reason did it give? Quote the lines of the output that show them.

> *doesn't say*  I can't confirm from memory that English Wikipedia has an article identifying the composer of "Persian Surgery Dervishes" or giving that person's birth date, so I can't verify the claim.

## 0c. Give it one search

Which Wikipedia page did it read? Quote the line of the output that shows it.

>  Page: Persian Surgery Dervishes

Did that page settle the claim correctly? If not, why do you think the search led there?

> No, it was not to identify the composer of the song from this page. It correctly recognized that the page did not mention Terry Riley's birthday. So, the verdict is 'doesn't say'. It could have checked Terry Riley's Wikipedia page. 

## 0d. Run the agent and read its trace

In one or two sentences, how did the agent get from the claim to its verdict? Point to the trace entries by their numbers.

> 1. queries for the composer of 'Persian Surgery Dervishes'; 2. reads for the composer Terry Riley; 3. reads the page for Terry Riley to find his birthday; 4. cumulates an answer that the album "Persian Surgery Dervishes" is by Terry Riley, and his Wikipedia article states he was born June 24, 1935.

Which lookup would you have done differently, and how? If none, which one surprised you?

> I am surprised that the query was able to find the composer through the song he composed and pulled the composer's bio through a different page. One thing I would have done differently was phrase the explanation to focus more on Terry Riley, not the song he composed. 

Describe Wikidata briefly. Why may it be important to this task?

> Wikidata stores facts in a fixed shape instead of a prose. It is important to this task because it is able to isolate necessary information through an item, a property, and a value. 

# Part 1: How the agent works

## 1a. Design the loop

Your loop should repeatedly call the model with the message history so far, and ask for its next step. It should check whether the model has given an answer yet. If not, it should make the lookups that step asks for, and add what they return to the history. It should also pay attention to whether the loop has reached its limit: a claim that runs out of lookups cannot be decided. One limit is set for you: 12 lookups for a claim.

The Background and an example outline are under 1a on the homework page, and in [instructions/part1.md](instructions/part1.md#1a-design-the-loop).

Write your outline of the loop in the code block: what it remembers, what it repeats, and every way it stops.

```
Set the count of lookups to 0.
Ask the model the question, and to pick items, properties, and values worth searching for. 
Store the model's reply.
If the reply gives an answer, stop and return that answer and the count of lookups, even if the reply also asks for searches or reads.
If the reply asks for any searches or reads:
    If the count of lookups has reached its limit, stop with no answer and return the number of lookups.
    Make every search and read that reply asked for.
    Add the number of searches and reads that were just made to the count of lookups.
    Store what came back from all of them.
    Give the model everything that came back, all together, and ask it again.
    Store the model's new reply and go back to "If the reply gives an answer".
If the reply has neither an answer nor any searches or reads:
    Remind the model to answer the question, and ask it again.
    Store the model's new reply and go back to "If the reply gives an answer".
```

List each thing your loop remembers from one turn to the next, and say what would go wrong without it.

> My loop remembers the important items, properties, and values in the question to help query necessary information. What could go wrong without it is that the loop would not focus on the information it needs to be extracting, it won't stay focused on answering the question.

Now open `reference_loop.py` and compare it with your loop. Describe one difference in implementation and the resulting effects on agent behavior.

> I was imagining there to be more manual callings of asking the model for an answer. But, under the variable talk, the model was called upon without a lot of direction from the loop. I think it made me realize that agent behavior relies upon the instructions set in system and the client Anthropic. I think what I wrote in the design of the loop was diluted in a way that goes to show that this particular agent's behavior is instructed simply in its real application.

## 1b. Be the agent

The claim: "Vic & Anthony's Steakhouse is located at the American casino that was combined with the California Club. The casino is owned by Landry's, Inc."

List your lookups, in order. Ask Claude to paste every column but the last from `runs/part1/lookups.jsonl`. Type "Why you chose it" yourself.

| # | Tool | What you asked for | Why you chose it |
|---|---|---|---|
| 1 | search | Vic & Anthony's Steakhouse | It checks to ensure the Steakhouse exists and will lead me to find the casino name | 
| 2 | read | Vic & Anthony's Steakhouse | Reads the casino name |
| 3 | search | Golden Nugget Casinos | Looks for information on California Club and Vic & Anthony's Steakhouse finds its Las Vegas Location|
| 4 | search | Califonia Club | Looks for Golden Nugget Casinos confirms its Las Vegas location |
| 5 | search | Golden Nugget Casino | Null on California Club and the Steakhouse existing at the location |
| 6 | read | Golden Nugget Las Vegas | Looks for information on Laudry's, Inc and confirms |
| 7 | wikidata | California club, property: location | Geospatial location of the club |
| 8 | wikidata | Golden Nugget Las Vegas, property: location | Compares Golden Nugget Las Vegas to the Califronia Club property |


What is your verdict on the claim, and which sentence or sentences from what you read is it based on?

>  I can only confirm that Vic & Anthony's Steakhouse exists in Las Vegas at the Golden Nugget Casino. The casino is owned by Landry's, Inc. I can show the location of California Club in relation to the location of the casino.

## 1c. Watch the agent work

List the three traces you read closely. At least one should be a claim the agent got wrong (if it got any wrong).

| # | Claim (first few words) | Articles | Did it match the dataset's label? | Did it get there for a good reason? Why or why not |
|---|---|---|---|---|
| 1 | Four operas | Krzysztof Pendereck | No | Yes, the composer does not compose operas |
| 2 | The actor | Paul Gross, Martha Burns | No | I think it was because of how the claim was phrased with past tense, 'had'. The relationship still persists |
| 3 | This Singapore | Detail (music producer), Drunk in Love, Joseph Schooling, Michael Phelps, We Dem Boyz| No | I think it messed up when it looked up what a music producer was and narrowed into a random song by Beyonce. It led itself to not be able to answer this question. |

Which trace did you find most interesting, and what did the agent do well or badly in it?

> I found the last trace to be the most interesting because I don't understand what the claim means. I think the agent should have looked to find 'freestyle' under a song produced by Detail. Instead of going to define a music producer. While there is no correlation that exists between Michael Phelps and any producer Detail, I think the agent could have done this in a different way to save lookups.

## 1d. Write the agent's instructions

What changed in the agent's traces after you wrote your instructions? Give one claim as an example.

> Not much changed in the results of the claims, but for the claim I spoke about in 1c, the agent did a much better job at navigating its queries. “Detail production credits song lyric "Singapore"” this query was what would have answered the claim.

## 1e. Start the full run, and predict

Predict the share of claims each version will get right (its verdict matches the dataset's label), as a percentage. A guess is fine; the reasons are what I grade.

| Version | 2 articles | 3 articles | 4 articles | Why you think so |
|---|---|---|---|---|
| No tools | 50% | 30% | 20% | I think it would access as many articles because of its limitations, and how it will pick what it can assess from the claim. |
| One search | 40% | 40% | 20% | I think it will lean more on articles because it is able to access one search with the claim opening up more options of items/properties/values to read on. |
| Agent | 20% | 30% | 50% | I think the agent will either be able to rationalize its lookups and read from less articles, but when the claim is confusing, the agent tends to derail from the topic of the claim and read more. |

How many lookups will the agent make per claim, on average? Why?

> I think the agent will make around 7 lookups per claim on average, because that is around what the agent did in previous exercises. 

# Part 2: The agent against the baselines

## 2a. Compare accuracy

Ask Claude to paste the report of your full run, from `runs/part2/report.txt`, into the empty block below.

```
```

How do the results compare with your predictions? Where were you furthest off? Use the numbers from your run, by number of articles.

>

Does the gap between the agent and the one-search baseline grow with the number of articles? What in the claims or the traces explains what you see?

>

The no-tools baseline read nothing. How did it do, and what does that tell you about these claims?

>

## 2b. Check the evidence yourself

Fill in one row for each of the first five claims in your full run, in the order of the claims file, where the agent's verdict is *supported* or *refuted*.

| # | Claim (first few words) | Agent's verdict | Matched the dataset's label? | Does the quoted evidence support that verdict? | Why or why not |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

Of the five, how many matched the dataset's label, and for how many of those does the quoted evidence support the verdict?

>

Is accuracy alone a good measure of this agent? Why or why not?

>

# Part 3 (extra credit): Why the agent fails, and one change

## 3a. Sort the failures

Fill in one row for each of the first eight failures in your full run, rows 1 to 8 of the claims table for runs/part2 with "Result" in "The agent" box set to "does not match the dataset's label (any reason)". If you have fewer than eight, fill a row for each and delete the rest.

| Row | Claim (first few words) | Your label | The entry of the trace that shows it | Is the dataset's label right? (yes, no or can't tell) | Claude's label |
|---|---|---|---|---|---|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |
| 6 | | | | | |
| 7 | | | | | |
| 8 | | | | | |

Where did you and Claude disagree, and who do you think is right?

>

Which kind of failure was most common? If no kind repeats, say which failure you will aim at in 3b, and why.

>

## 3b. Make one change

What did you change, and why did you expect it to help?

>

How many of your evaluation claims did the agent match before the change and after it? Which of your failures from 3a now match?

>

Quote one claim the agent matched before the change and not after it, if there is one, and say what you think happened. If there is none, say so.

>

## 3c. Write it up

What does the agent's loop add over one search, what does it cost, and when would you not use an agent for a job like this? Use your numbers from Part 2 and Part 3.

>

What did your claims show you about Wikipedia as a source? Where it was thin or wrong, why might that be, given who writes it?

>

Your numbers rest on 100 claims. Which of your conclusions would you trust on another 100 claims, which might be chance, and what would you measure to find out?

>
