from dnslib import DNSRecord, DNSHeader, RR, A, QTYPE
from dnslib.server import DNSServer, BaseResolver
import socket


class LocalResolver(BaseResolver):
    def __init__(self, local_ip):
        self.local_ip = local_ip

    def resolve(self, request, handler):
        reply = request.reply()
        qname = str(request.q.qname)

        # Handle picotrip.local.com
        if 'picotrip.local.com' in qname:
            reply.add_answer(RR(qname, QTYPE.A, rdata=A(self.local_ip), ttl=60))
        else:
            # Forward to Google DNS
            try:
                upstream = DNSRecord.parse(DNSRecord.question(qname).send('8.8.8.8', 53))
                for rr in upstream.rr:
                    reply.add_answer(rr)
            except:
                pass

        return reply


if __name__ == '__main__':
    # Get your local IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()

    print(f"Starting DNS server for picotrip.local.com -> {local_ip}")
    print(f"Configure your mobile DNS to: {local_ip}")

    resolver = LocalResolver(local_ip)
    server = DNSServer(resolver, port=53, address='0.0.0.0')
    server.start()