using UCHBot;

CancellationTokenSource ct = new();

Console.CancelKeyPress += (sender, eventArgs) =>
{
	ct.Cancel();
};

PathGeneratorClient pathGeneratorClient = new();
await pathGeneratorClient.StartPathFinderServer(ct.Token);


//var serializerSettings = new JsonSerializerSettings
//{
//	TypeNameHandling = TypeNameHandling.All,
//	Formatting = Formatting.Indented
//};

//StaticBlock block = new StaticBlock(0, 1, 1, new Vector2(), new Vector2(), CollisionType.Block);
//string serializeObject = JsonConvert.SerializeObject(block, serializerSettings);

//Console.WriteLine(serializeObject);