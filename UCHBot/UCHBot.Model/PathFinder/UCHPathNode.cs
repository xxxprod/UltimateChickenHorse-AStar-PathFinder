using UCHBot.Model.GameModels;

namespace UCHBot.Model.PathFinder;

public class UCHPathNode
{
	public int Segment { get; set; }

	public Vector2 Position { get; set; }
	public Vector2 Velocity { get; set; }
	public PlayerAction[] Actions { get; set; }
	
	public Vector2 RealVelocity { get; set; }
	public Vector2 RealPosition { get; set; }
	
	public string State { get; set; }

	public bool OnGround { get; set; }
	public bool OnWall { get; set; }
}