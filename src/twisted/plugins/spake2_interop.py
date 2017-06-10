from twisted.application.service import ServiceMaker

spake2_interop = ServiceMaker("spake2_interop",
                              "spake2_interop_server.server",
                              "SPAKE2 interoperability testing server",
                              "spake2_interop")
