using UCHBot.Model.GameModels.Blocks;

namespace UCHBot.Model.GameModels;

public class LevelModel
{
	public BlockCollection Blocks { get; }
	public StaticBlock[] Goals { get; }

	public LevelModel(BlockCollection blocks)
	{
		Blocks = blocks;
		Goals = Blocks.Where(b => b.CollisionType is CollisionType.Goal).ToArray();
	}


	public static LevelModel LoadFromXml(string path)
	{
		XmlDocument xml = new();
		xml.Load(path);

		return LoadFromXml(xml);
	}

	public static LevelModel LoadFromXml(XmlDocument xml)
	{
		StaticBlock[] blocks = xml.GetNodes("./block")
			.Concat(xml.GetNodes("./moved"))
			.Select(ParseXmlBlock)
			.Where(block => block != null)
			.SelectMany(a => a.GetStaticBlocks())
			.ToArray();

		LevelBorderBlock[] borderBlocks = blocks.OfType<LevelBorderBlock>().ToArray();
		StaticBlock leftBorder = borderBlocks.Single(a => a.CollisionType == CollisionType.LeftBorder);
		StaticBlock rightBorder = borderBlocks.Single(a => a.CollisionType == CollisionType.RightBorder);
		StaticBlock topBorder = borderBlocks.Single(a => a.CollisionType == CollisionType.TopBorder);
		StaticBlock bottomBorder = borderBlocks.Single(a => a.CollisionType == CollisionType.DeathPit);

		leftBorder.Bounds = new Bounds(
			leftBorder.Bounds.Position.X,
			bottomBorder.Bounds.Position.Y,
			leftBorder.Bounds.Size.X,
			topBorder.Bounds.Position.Y - bottomBorder.Bounds.Position.Y
		);

		rightBorder.Bounds = new Bounds(
			rightBorder.Bounds.Position.X,
			bottomBorder.Bounds.Position.Y,
			rightBorder.Bounds.Size.X,
			topBorder.Bounds.Position.Y - bottomBorder.Bounds.Position.Y
		);

		bottomBorder.Bounds = new Bounds(
			leftBorder.Bounds.Position.X,
			bottomBorder.Bounds.Position.Y,
			rightBorder.Bounds.Position.X - leftBorder.Bounds.Position.X,
			bottomBorder.Bounds.Size.Y
		);

		topBorder.Bounds = new Bounds(
			leftBorder.Bounds.Position.X,
			topBorder.Bounds.Position.Y,
			rightBorder.Bounds.Position.X - leftBorder.Bounds.Position.X,
			topBorder.Bounds.Size.Y
		);

		return new LevelModel(new BlockCollection(blocks));
	}

	private static IBlock ParseXmlBlock(XmlNode xmlNode)
	{
		if (StaticBlock.TryParse(xmlNode, out IBlock block))
			return block;

		if (StartBlock.TryParse(xmlNode, out block))
			return block;

		if (GoalBlock.TryParse(xmlNode, out block))
			return block;

		if (LevelBorderBlock.TryParse(xmlNode, out block))
			return block;

		if (WoodBlock.TryParse(xmlNode, out block))
			return block;

		if (LBlock.TryParse(xmlNode, out block))
			return block;

		if (ScaffoldBlock.TryParse(xmlNode, out block))
			return block;

		if (BarrelBlock.TryParse(xmlNode, out block))
			return block;

		if (HayBlock.TryParse(xmlNode, out block))
			return block;

		if (WireBlock.TryParse(xmlNode, out block))
			return block;

		if (SpikeBlock.TryParse(xmlNode, out block))
			return block;

		throw new NotImplementedException($"Element {xmlNode.OuterXml} not supported.");
	}

	public bool IsBlocked(Bounds bounds, float margin)
	{
		return Blocks.Any(b => b.Bounds.Intersects(bounds, margin));
	}
}