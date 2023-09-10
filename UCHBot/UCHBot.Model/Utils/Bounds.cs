namespace UCHBot.Model.Utils;

[DebuggerDisplay("Left: {Left}, Top: {Top}, Right: {Right}, Bottom: {Bottom}")]
public readonly struct Bounds
{
    public readonly Vector2 Position;
    public readonly Vector2 Size;
    public float Left => Position.X;
    public float Right => Position.X + Size.X;
    public float Top => Position.Y + Size.Y;
    public float Bottom => Position.Y;
    public float CenterX => Left + Size.X / 2;
    public float CenterY => Top - Size.Y / 2;
    public Vector2 Center => new(CenterX, CenterY);

    public Bounds(Vector2 position, Vector2 size)
    {
        Position = position;
        Size = size;
    }

    public Bounds(float x, float y, float width, float height)
    {
        Position = new Vector2(x, y);
        Size = new Vector2(width, height);
    }

    public bool Intersects(Bounds other, double margin)
    {
        if (Right <= other.Left - margin || other.Right <= Left - margin)
            return false;

        if (other.Top <= Bottom - margin || Top <= other.Bottom - margin)
            return false;

        return true;
    }

    //public bool Overlaps(Bounds other)
    //{
    //    if (Right < other.Left || other.Right < Left)
    //        return false;

    //    if (other.Top < Bottom || Top < other.Bottom)
    //        return false;

    //    return true;
    //}

    public Bounds Translate(Vector2 offset)
    {
        return new Bounds(Position + offset, Size);
    }

    public override string ToString()
    {
	    return $"[({Position.X}, {Position.Y}), ({Size.X}, {Size.Y})]";
    }
}