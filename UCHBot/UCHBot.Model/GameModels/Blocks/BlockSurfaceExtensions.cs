namespace UCHBot.Model.GameModels.Blocks;

public static class BlockSurfaceExtensions
{
    private const double Epsilon = 0.1;

    public static IEnumerable<BlockSurface> Merge(this IEnumerable<BlockSurface> surfaces)
    {
        return MergeHorizontalSurfaces(MergeVerticalSurfaces(surfaces));
    }

    private static IEnumerable<BlockSurface> MergeHorizontalSurfaces(IEnumerable<BlockSurface> surfaces)
    {
        BlockSurface first = null;
        Bounds b1 = default;

        foreach (BlockSurface current in surfaces
                     .OrderBy(a => a.Bounds.Top)
                     .ThenBy(a => a.Bounds.Left))
        {
            if (first == null)
            {
                first = current;
                b1 = first.Bounds;
                continue;
            }
            if (first.Face is not BlockFace.Top)
            {
                yield return first;
                first = current;
                b1 = first.Bounds;
                continue;
            }
            if (current.Face is not BlockFace.Top)
            {
                yield return current;
                continue;
            }

            Bounds b2 = current.Bounds;

            bool sameRow = Math.Abs(b2.Top - b1.Top) < Epsilon;
            bool connecting = Math.Abs(b1.Right - b2.Left) < Epsilon;
            bool intersecting = b2.Intersects(b1, 0.1f);
            bool sameKind = first.Face == current.Face && first.CollisionType == current.CollisionType;
            bool prevBefore = b1.Left < b2.Left;

            if (!sameRow || !(connecting && sameKind) && !intersecting)
            {
                yield return new BlockSurface(first.Face, first.CollisionType, b1);
                first = current;
                b1 = first.Bounds;
                continue;
            }

            if (sameKind)
            {
                float minLeft = Math.Min(b2.Left, b1.Left);
                float maxRight = Math.Max(b2.Right, b1.Right);

                b1 = new Bounds(minLeft, b1.Bottom, maxRight - minLeft, b1.Size.Y);
                continue;
            }

            if (prevBefore)
            {
                yield return new BlockSurface(first.Face, first.CollisionType,
                    new Bounds(b1.Left, b1.Bottom, b2.Left - b1.Left, b1.Size.Y));

                b1 = new Bounds(b2.Left, b1.Bottom, b1.Right - b2.Left, b1.Size.Y);
            }

            if (b1.Right > b2.Right)
                b1 = new Bounds(b2.Right, b1.Bottom, b1.Right - b2.Right, b1.Size.Y);
            else if (b1.Right < b2.Right)
            {
                first = current;
                b1 = new Bounds(b1.Right, b1.Bottom, b2.Right - b1.Right, b1.Size.Y);
            }
            else
            {
                first = null;
            }
        }

        if (first != null)
            yield return new BlockSurface(first.Face, first.CollisionType, b1);
    }

    private static IEnumerable<BlockSurface> MergeVerticalSurfaces(IEnumerable<BlockSurface> surfaces)
    {
        BlockSurface first = null;
        Bounds b1 = default;

        foreach (BlockSurface current in surfaces
                     .OrderBy(a => a.Bounds.Left)
                     .ThenBy(a => a.Bounds.Bottom))
        {
            if (first == null)
            {
                first = current;
                b1 = first.Bounds;
                continue;
            }

            if (first.Face is not (BlockFace.Left or BlockFace.Right))
            {
                yield return first;
                first = current;
                b1 = first.Bounds;
                continue;
            }
            if (current.Face is not (BlockFace.Left or BlockFace.Right))
            {
                yield return current;
                continue;
            }

            Bounds b2 = current.Bounds;

            bool sameCol = Math.Abs(b2.Left - b1.Left) < Epsilon;
            bool connecting = Math.Abs(b1.Top - b2.Bottom) < Epsilon;
            bool intersecting = b2.Intersects(b1, 0.1f);
            bool sameKind = first.Face == current.Face && first.CollisionType == current.CollisionType;

            if (!sameCol || !(connecting && sameKind) && !intersecting)
            {
                yield return new BlockSurface(first.Face, first.CollisionType, b1);
                first = current;
                b1 = first.Bounds;
                continue;
            }

            if (sameKind)
            {
                float minBottom = Math.Min(b2.Bottom, b1.Bottom);
                float maxTop = Math.Max(b2.Top, b1.Top);

                b1 = new Bounds(b1.Left, minBottom, b1.Size.X, maxTop - minBottom);
                continue;
            }

            if (b1.Bottom < b2.Bottom)
            {
                yield return new BlockSurface(first.Face, first.CollisionType,
                    new Bounds(b1.Left, b1.Bottom, b1.Size.X, b2.Bottom - b1.Bottom));

                b1 = new Bounds(b1.Left, b2.Bottom, b1.Size.X, b1.Top - b2.Bottom);
            }

            if (b1.Top > b2.Top)
            {
                b1 = new Bounds(b1.Left, b2.Top, b1.Size.X, b1.Top - b2.Top);
            }
            else if (b1.Top < b2.Top)
            {
                first = current;
                b1 = new Bounds(b1.Left, b1.Top, b1.Size.X, b2.Top - b1.Top);
            }
            else
            {
                first = null;
            }
        }

        if (first != null)
            yield return new BlockSurface(first.Face, first.CollisionType, b1);
    }

    public static IEnumerable<BlockSurface> Split(this BlockSurface surface, BlockSurfaceSplitOptions options) => surface.Split(options.Width, options.Height,
        options.StepX, options.StepY, options.OffsetX, options.OffsetY);

    public static IEnumerable<BlockSurface> Split(this BlockSurface surface,
        float width, float height,
        float stepX, float stepY,
        float offsetX, float offsetY)
    {
        Bounds b = surface.Bounds;
        if (surface.Face is BlockFace.Top)
        {
            float x = b.Left - offsetX;
            for (; x < b.Right - width + offsetX - 0.01f; x += stepX)
            {
                yield return new BlockSurface(surface.Face, surface.CollisionType, new Bounds(x, b.Bottom, width, b.Size.Y));
            }

            yield return new BlockSurface(surface.Face, surface.CollisionType, new Bounds(b.Right - width + offsetX, b.Bottom, width, b.Size.Y));
        }
        else
        {
            float y = b.Bottom - offsetY;
            for (; y < b.Top - height + offsetY - 0.01f; y += stepY)
            {
                yield return new BlockSurface(surface.Face, surface.CollisionType, new Bounds(b.Left, y, b.Size.X, height));
            }

            yield return new BlockSurface(surface.Face, surface.CollisionType, new Bounds(b.Left, b.Top - height + offsetY, b.Size.X, height));
        }
    }
}