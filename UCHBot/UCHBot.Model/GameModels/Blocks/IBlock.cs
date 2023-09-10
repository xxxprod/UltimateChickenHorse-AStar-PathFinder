namespace UCHBot.Model.GameModels.Blocks;

public interface IBlock
{
    IEnumerable<BlockSurface> GetSurfaces(Bounds other = default);
    IEnumerable<StaticBlock> GetStaticBlocks();
}