using UCHBot.Model;

namespace UCHBot.Shared.Events;

public class LevelLoadedEvent : GameEvent.GameEvent
{
	public LevelModel LevelModel { get; }

	public LevelLoadedEvent(LevelModel levelModel)
	{
		LevelModel = levelModel;
	}
}