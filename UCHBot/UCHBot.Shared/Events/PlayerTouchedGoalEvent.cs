namespace UCHBot.Shared.Events;

public class PlayerTouchedGoalEvent : GameEvent.GameEvent
{
    public Character Character { get; }

    public PlayerTouchedGoalEvent(Character character)
    {
        Character = character;
    }
}