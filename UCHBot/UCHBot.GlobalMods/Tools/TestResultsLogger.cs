using System.IO;
using Newtonsoft.Json;

namespace UCHBot.GlobalMods.Tools;

public static class TestResultsLogger
{
	public const string LogPath = "../DataAnalysis/TestResults";

	static TestResultsLogger()
	{
		if (!Directory.Exists(LogPath))
			Directory.CreateDirectory(LogPath);
	}

	public static T LoadData<T>(string fileName)
	{
		return JsonConvert.DeserializeObject<T>(File.ReadAllText($"{LogPath}\\{fileName}", Encoding.UTF8));
	}

	public static void LogResults(string logName, object results, bool withLogTime)
	{
		if (withLogTime)
			File.WriteAllText($"{LogPath}/{logName}_{DateTime.UtcNow:yyyy-MM-dd_HH-mm-ss}.json", JsonConvert.SerializeObject(results, Formatting.Indented));
		else
			File.WriteAllText($"{LogPath}/{logName}.json", JsonConvert.SerializeObject(results, Formatting.Indented));
	}
}