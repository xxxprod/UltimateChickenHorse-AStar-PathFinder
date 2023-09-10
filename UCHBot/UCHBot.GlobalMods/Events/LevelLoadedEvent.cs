using UCHBot.Model;
using UCHBot.Model.GameModels;

namespace UCHBot.GlobalMods.Events;

public class LevelLoadedEvent : GameEvent.GameEvent
{
	public LevelModel LevelModel { get; }

	public LevelLoadedEvent(LevelModel levelModel)
	{
		LevelModel = levelModel;
	}
}