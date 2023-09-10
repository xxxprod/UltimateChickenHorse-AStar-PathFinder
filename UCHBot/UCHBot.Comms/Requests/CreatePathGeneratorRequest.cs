namespace UCHBot.Comms.Requests;

public class CreatePathGeneratorRequest
{
	public const string RequestKey = "getPathGeneratorRequest";

	public string LevelCode { get; set; }
}