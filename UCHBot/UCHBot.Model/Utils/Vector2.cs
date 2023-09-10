namespace UCHBot.Model.Utils;

public readonly struct Vector2
{
	public Vector2(float x, float y)
	{
		X = x;
		Y = y;
	}

	public float X { get; }
	public float Y { get; }

	public static Vector2 operator +(Vector2 a, Vector2 b)
	{
		return new Vector2(a.X + b.X, a.Y + b.Y);
	}
}