using UCHBot.Model.PathFinder;

namespace UCHBot.Comms.Requests;


public abstract class PathRequestBase
{
	public UCHPath[] Paths { get; set; }
}

public class ShowPathRequest : PathRequestBase
{
	public const string RequestKey = "showPath";
}

public class ExecuteGeneratedPathRequest : PathRequestBase
{
	public const string RequestKey = "executePath";
}


public class ExecutedPathResults : PathRequestBase
{
	public const string RequestKey = "executedPathResults";
}