using System.Net;
using System.Net.Sockets;
using System.Threading;
using System.Threading.Tasks;
using BepInEx;
using Newtonsoft.Json;
using UCHBot.Comms;
using UCHBot.Comms.Requests;
using UCHBot.GlobalMods.Tools;

namespace UCHBot.GlobalMods.Mods;

public interface ICommunicationServer
{
	void RegisterMessageHandler<T>(string messageTypeName, Action<T> handler);
	public void Send<T>(T data);
}

[BepInPlugin(nameof(CommunicationServer), nameof(CommunicationServer), "1.0.0")]
public class CommunicationServer : BaseUnityPlugin, ICommunicationServer
{
	public const bool Verbose = false;

	private readonly Dictionary<string, Type> _messageTypeMappings = new();
	private readonly Dictionary<Type, string> _messageTypeMappingsReverse = new();
	private readonly Dictionary<Type, List<Delegate>> _messageTypeHandlers = new();


	private TcpListener _tcpListener;
	private CommunicationClient _client;
	private Task _receiverTask;

	public static ICommunicationServer Instance { get; private set; }


	private void OnEnable()
	{
		_tcpListener = new TcpListener(IPAddress.Loopback, 4711);
		_tcpListener.Start();
		_ = StartListener();

		Instance = this;

		Instance.RegisterMessageHandler<KeepAliveRequest>(KeepAliveRequest.RequestKey, request =>
		{
			_client.KeepAlive();
		});
	}

	private async Task StartListener()
	{
		while (_tcpListener != null)
		{
			try
			{
				if (_tcpListener.Pending())
				{
					if (_client == null || _receiverTask.IsCompleted)
					{
						_client?.Dispose();

						UCHTools.Log($"Accepting new Client Connection");

						_client = new CommunicationClient(await _tcpListener.AcceptSocketAsync(),
							message => UCHTools.Log(message));
						_receiverTask = _client.StartReceiving(SendMessage, CancellationToken.None);
					}
					else
					{
						UCHTools.Log("ERROR: Client already connected! Shutting down other client.");
						_client.Dispose();
					}
				}
			}
			catch (Exception e)
			{
				UCHTools.Log("Error: " + e.Message + e.StackTrace);
				_client?.Dispose();
				_receiverTask?.Dispose();
			}

			await Task.Delay(1000);
		}
	}

	private void SendMessage(string messageType, string message)
	{
		try
		{
			_ = messageType ?? throw new ArgumentException("No MessageType delivered");

			if (!_messageTypeMappings.TryGetValue(messageType, out Type serializationType) ||
				!_messageTypeHandlers.TryGetValue(serializationType, out List<Delegate> messageHandlers))
				throw new InvalidOperationException($"Unknown MessageType {messageType}");

			object deserialized = JsonConvert.DeserializeObject(message, serializationType);

			foreach (Delegate messageHandler in messageHandlers)
				messageHandler.DynamicInvoke(deserialized);
		}
		catch (Exception e)
		{
			UCHTools.Log($"Error parsing and sending message: {message}");
			UCHTools.Log("Error: " + e.Message + e.StackTrace);
		}
	}

	private void OnDisable()
	{
		_tcpListener.Stop();
		_tcpListener.Server.Dispose();
		_tcpListener = null;
	}

	public void Send<T>(T data)
	{
		if (_client == null)
			throw new InvalidOperationException("No Client connected");

		if (!_messageTypeMappingsReverse.TryGetValue(typeof(T), out string messageType))
			throw new InvalidOperationException($"Unknown MessageType {typeof(T)}");

		try
		{
			_client.Send(messageType, data);
		}
		catch (Exception e)
		{
			UCHTools.Log($"Error sending message: {messageType} {data}");
			UCHTools.Log("Error: " + e.Message + e.StackTrace);
			_client.Dispose();
			_client = null;
		}
	}

	public void RegisterMessageHandler<T>(string messageTypeName, Action<T> handler)
	{
		_messageTypeMappings[messageTypeName] = typeof(T);
		_messageTypeMappingsReverse[typeof(T)] = messageTypeName;

		if (!_messageTypeHandlers.TryGetValue(typeof(T), out List<Delegate> messageHandlers))
			_messageTypeHandlers.Add(typeof(T), messageHandlers = new List<Delegate>());

		messageHandlers.Add(handler);
	}
}