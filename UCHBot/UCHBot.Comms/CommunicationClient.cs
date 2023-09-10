using System;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace UCHBot.Comms;

public class CommunicationClient : IDisposable
{
	private readonly Action<string> _logger;
	private const int MessageTypeSeparator = 30;
	private const int MessageSeparator = 31;

	private DateTime _lastCommunication;
	private readonly byte[] _buffer = new byte[1024 * 1024 * 100];
	public Socket Socket { get; }

	private TimeSpan ClientTimeout = TimeSpan.FromSeconds(10);

	public CommunicationClient(Socket socket, Action<string> logger)
	{
		_logger = logger;
		Socket = socket;
		_lastCommunication = DateTime.Now;
		new JsonSerializerSettings
		{
			TypeNameHandling = TypeNameHandling.All
		};
	}

	public async Task StartReceiving(Action<string, string> messageReceivedCallback, CancellationToken cancellationToken)
	{
		_logger("Starting to receive messages");

		while (!cancellationToken.IsCancellationRequested)
		{
			try
			{
				if (Socket.Available == 0)
				{
					if (DateTime.Now - _lastCommunication > ClientTimeout)
						break;

					await Task.Delay(100, CancellationToken.None);
					continue;
				}

				int length = Socket.Receive(_buffer, 0, _buffer.Length, SocketFlags.None);
				int start = 0;
				string messageType = null;

				for (int i = 0; i < length; i++)
				{
					switch (_buffer[i])
					{
						case MessageTypeSeparator:
							messageType = Encoding.UTF8.GetString(_buffer, start, i - start);
							start = i + 1;
							break;
						case MessageSeparator:
							string message = Encoding.UTF8.GetString(_buffer, start, i - start);

							_logger($"Received {messageType}");
							messageReceivedCallback(messageType, message);
							start = i + 1;
							messageType = null;
							break;
					}
				}

				if (messageType != null || start < length)
				{
					throw new InvalidOperationException("Message incomplete");
				}


				_lastCommunication = DateTime.Now;
			}
			catch (Exception e)
			{
				_logger(e.Message);
				break;
			}
		}

		_logger("Stopped receiving messages");
	}

	public void Send<T>(string messageKey, T data)
	{
		_logger($"Sending {messageKey}");

		byte[] message = Encoding.UTF8.GetBytes(
			$"{messageKey}{(char)MessageTypeSeparator}{JsonConvert.SerializeObject(data)}{(char)MessageSeparator}");

		Socket.Send(message);
		_lastCommunication = DateTime.Now;
	}

	public void KeepAlive()
	{
		ClientTimeout = TimeSpan.MaxValue;
	}

	public void Dispose()
	{
		Socket?.Dispose();
	}

	public static CommunicationClient Connect(string host, int port, Action<string> loggingCallback)
	{
		Socket socket = new(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
		socket.Connect(host, port);

		return new CommunicationClient(socket, loggingCallback);
	}
}