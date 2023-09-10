using Newtonsoft.Json;
using UCHBot.Comms.Requests;

namespace UCHBot.Tests
{
	public class UnitTest1
	{
		[Fact]
		public void Test1()
		{
			string json= """
{'Paths':[{'Nodes':[{'Position': { 'X': 10, 'Y': 11 },'Velocity': { 'X': 0.1, 'Y': 0.2 },'Action': 5}]}]}
""";
			ExecuteGeneratedPathRequest o = JsonConvert.DeserializeObject<ExecuteGeneratedPathRequest>(json);

		}
	}
}