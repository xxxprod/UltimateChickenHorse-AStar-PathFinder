namespace UCHBot.Model.GameModels;

[DebuggerDisplay("Player: {Bounds}")]
public class PlayerModel
{
	public static readonly Vector2 Size = new(0.89f, 1.60f);
	public static readonly Vector2 PositionOffset = new((1 - Size.X) / 2, -0.90f);

	public Bounds Bounds { get; }

	public PlayerModel(Vector2 position)
	{
		position = new Vector2(position.X, position.Y);
		position += PositionOffset;
		Bounds = new Bounds(position, Size).Translate(new Vector2(-0.5f, 0.5f));
	}
}