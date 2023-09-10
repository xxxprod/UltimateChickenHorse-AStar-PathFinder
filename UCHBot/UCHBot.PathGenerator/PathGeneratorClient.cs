using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using UCHBot.Comms;
using UCHBot.Comms.Requests;
using UCHBot.Model.GameModels;
using UCHBot.Model.PathFinder;
using UCHBot.Model.Utils;
using UCHBot.Utils;

namespace UCHBot;

public class PathGeneratorClient
{
	private CommunicationClient _uchServer;

	public async Task StartPathFinderServer(CancellationToken cancellationToken)
	{
		_uchServer = CommunicationClient.Connect("localhost", 4711, Log.WriteLine);

		cancellationToken.Register(() => _uchServer.Dispose());

		Task receiverTask = _uchServer.StartReceiving((messageKey, message) =>
		{
			if (messageKey == GeneratePathRequest.RequestKey)
			{
				GeneratePathRequest generatePathRequest = JsonConvert.DeserializeObject<GeneratePathRequest>(message);

				UCHPath path = GeneratePath(generatePathRequest);

				SendExecutePathRequest(path);
			}
		}, cancellationToken);

		Task pingTask = Task.Run(async () =>
		{

			while (!receiverTask.IsCompleted)
			{
				_uchServer.Send(ServerPingRequest.RequestKey, new ServerPingRequest());

				await Task.Delay(1000, CancellationToken.None);
			}
		}, cancellationToken);

		while (true)
		{
			await Task.Delay(1000, CancellationToken.None);

		}
	}

	private UCHPath GeneratePath(GeneratePathRequest generatePathRequest)
	{
		return new UCHPath
		{
			Nodes = new List<UCHPathNode>
			{
				new() { Position = new Vector2(-12, -5), Actions = new[] { PlayerAction.Jump, } },
				new() { Position = new Vector2(-20, -1), Actions = new[] { PlayerAction.Jump, } },
				new() { Position = new Vector2(-22, -9), Actions = new[] { PlayerAction.Jump, } }
			}
		};
	}

	private void SendShowPathRequest(params UCHPath[] paths)
	{
		_uchServer.Send(ShowPathRequest.RequestKey, new ShowPathRequest { Paths = paths });
	}

	private void SendExecutePathRequest(params UCHPath[] paths)
	{
		_uchServer.Send(ExecuteGeneratedPathRequest.RequestKey, new ExecuteGeneratedPathRequest { Paths = paths });
	}
}