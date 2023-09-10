using UnityEngine;

namespace UCHBot.TestMod;

public class TestScenario
{
	public string LevelName { get; set; }
	public Vector2 StartOffset { get; set; }
	public TestStep[] Steps { get; set; }
}