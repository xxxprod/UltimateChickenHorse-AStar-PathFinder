namespace UCHBot.Model.GameModels.Blocks;

public class BlockSurfaceSplitOptions
{
    public float Width{get;}
    public float Height{get;}
    public float StepX{get;}
    public float StepY{get;}
    public float OffsetX{get;}
    public float OffsetY{get; }

    public BlockSurfaceSplitOptions(float width, float height, float stepX, float stepY, float offsetX, float offsetY)
    {
        Width = width;
        Height = height;
        StepX = stepX;
        StepY = stepY;
        OffsetX = offsetX;
        OffsetY = offsetY;
    }
}