using UCHBot.Model.GameModels;

namespace UCHBot.Comms.Requests;

public class GeneratePathRequest
{
	public const string RequestKey = "generatePath";

	public LevelModel Level { get; }
	public PlayerModel Spawn { get; }

	public GeneratePathRequest(LevelModel level, PlayerModel spawn)
	{
		Level = level;
		Spawn = spawn;
	}
}