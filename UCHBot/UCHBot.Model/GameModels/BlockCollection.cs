using Newtonsoft.Json;
using UCHBot.Model.GameModels.Blocks;

namespace UCHBot.Model.GameModels;

[JsonArray(ItemTypeNameHandling = TypeNameHandling.All)]
public class BlockCollection : List<StaticBlock>
{
	public BlockCollection(IEnumerable<StaticBlock> blocks) : base(blocks)
	{
	}
}