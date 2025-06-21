Create a ReAct agent demo using latest version of LangChain and OpenAI o4 model to show case how to enforce
bussiness rules in an autonomous agent.

First, we track the agent state and update it in tool calls.

Secondly, we model business rules as python rules that are run at the start of tool calls.

Each business rule has the following component:
1. The predicate function that runs on current state
2. If the predicate check fails, it returns an explainable reason to LLM, so the LLM can replann accordingly and fail gracefully.
3. It has a general description that guides LLM for initial planning and will be rendered into the agent prompt.

We can write a mock scenario: let's say the user wants to choose for an activity (Play games, Go Camping, Swimming).

And the ploicies (rules) are:
1. The user must have a TV and an XBox before he can play games
2. The user must have Hiking Boots before he can go campling
3. The user must have Goggle before he can go swimming
4. If the weather is raining, the user cannot go camping
5. If the weather is snowing, the user cannot go swimming
6. If the weather is unknown, the user can only play games
7. If the weather is already known, the weather tool cannot be called again

The following tools are provided:
1. Check the weather, returns a random weather condition between sunny, raining, snowing
2. Shopping, mock API call to return the purchase that user has made
3. Choose an activity: mock Api call to store the user's choice of activity

Create a command line demo to show case how we can enforce business rules without hard code the workflows the 
agent has to follow.

Use best practices for python project layout and coding styles.