namespace UCHBot.Model.GameModels.Blocks;

[DebuggerDisplay("Start: {Bounds}")]
public class StartBlock : StaticBlock
{
    private static readonly Vector2 Size = new(4, 1);
    private static readonly Vector2 PositionOffset = new(-1.5f, -1);

    public StartBlock(int sceneId, int? parentId, Vector2 position) : base(sceneId, parentId, 0, position, Size,
        CollisionType.Block)
    {
    }

    public new static bool TryParse(XmlNode xmlNode, out IBlock block)
    {
        Debug.Assert(xmlNode.Attributes != null, "xmlNode.Attributes != null");

        block = null;
        if (xmlNode.Attributes.GetString("path") != "StartPlank")
            return false;
        
        int? parentId = GetParentId(xmlNode);

        Vector2 offset = PositionOffset;
        block = new StartBlock(-99, parentId, GetPosition(xmlNode) + offset);
        return true;
    }
}