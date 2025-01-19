# Function Call Profiling

I want to understand how the amount of function calls and parallelized function calls impact the speed of the llm response. This is not done scientifically, just a way for me to ballpark my understanding.

| Parallel   |   Tools | Complexity   | Tool Calls      |   Total Time (s) |   Tool Time (s) |
|------------|---------|--------------|-----------------|------------------|-----------------|
| No         |       1 | simple       | [1]             |             8.08 |      **5.58**   |
| No         |       2 | simple       | [1, 1]          |            11.26 |      **9.32**   |
| No         |       5 | simple       | [1, 1, 1, 1, 1] |            20.28 |      **18.43**  |
| Yes        |       1 | simple       | [1]             |             7.27 |      **5.43**   |
| Yes        |       2 | simple       | [2]             |            17.61 |      **15.36**  |
| Yes        |       5 | simple       | [5]             |             9.73 |      **7.88**   |
| No         |       1 | medium       | [1]             |             7.68 |      **5.81**   |
| No         |       2 | medium       | [1, 1]          |            10.39 |      **8.5**    |
| No         |       5 | medium       | [1, 1, 1, 1, 1] |            19.06 |      **17.11**  |
| Yes        |       1 | medium       | [1]             |             6.61 |      **4.56**   |
| Yes        |       2 | medium       | [2]             |             9.68 |      **6.45**   |
| Yes        |       5 | medium       | [5]             |             9.73 |      **7.68**   |
| No         |       1 | complex      | [1]             |             9.61 |      **7.68**   |
| No         |       2 | complex      | [1, 1]          |            13.07 |      **11.07**  |
| No         |       5 | complex      | [1, 1, 1, 1, 1] |            23.98 |      **22.32**  |
| Yes        |       1 | complex      | [1]             |             7.83 |      **5.22**   |
| Yes        |       2 | complex      | [2]             |            11.09 |      **9.26**   |
| Yes        |       5 | complex      | [5]             |            15.22 |      **13.54**  |

### Variables

#### Dynamic Variables
- Amount of tool calls
- How many tool calls are called in parallel
- Argument complexity

#### Constant Variables
- openai gpt-4o-mini
- small function tool response (to save on money)


