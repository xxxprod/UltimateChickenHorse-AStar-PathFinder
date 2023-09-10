using System.Collections.Generic;
using System.Linq;

namespace UCHBot.TestMod;

public static class TestScenarioExtensions
{
	public static TestScenario[] Flatten(this IEnumerable<TestScenario> scenarios)
	{
		return scenarios.SelectMany(FlattenScenario).ToArray();
	}

	private static TestScenario[] FlattenScenario(TestScenario scenario)
	{
		return FlattenSteps().Select(steps => new TestScenario
		{
			LevelName = scenario.LevelName,
			StartOffset = scenario.StartOffset,
			Steps = steps
		}).ToArray();

		IEnumerable<TestStep[]> FlattenSteps(int stepIdx = 0, List<TestStep> steps = null)
		{
			steps ??= new List<TestStep>();

			if (stepIdx >= scenario.Steps.Length)
			{
				yield return steps.ToArray();
				yield break;
			}

			TestStep step = scenario.Steps[stepIdx];
			if (step.RepeatCounts == null)
			{
				steps.Add(step);
				foreach (TestStep[] scenarioSteps in FlattenSteps(stepIdx + 1, steps))
					yield return scenarioSteps;
				steps.Remove(step);
			}
			else
			{
				foreach (int repeatCount in step.RepeatCounts)
				{
					TestStep newStep = new()
					{
						Actions = step.Actions,
						RepeatCount = repeatCount,
						PositionOffset = step.PositionOffset
					};

					steps.Add(newStep);
					foreach (TestStep[] scenarioSteps in FlattenSteps(stepIdx + 1, steps))
						yield return scenarioSteps;
					steps.Remove(newStep);
				}
			}
		}
	}
}