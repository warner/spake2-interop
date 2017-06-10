from twisted.application.service import ServiceMaker

serviceMaker = ServiceMaker("spake2_interop",
                            "spake2_interop_server.server",
                            "SPAKE2 interoperability testing server",
                            "spake2_interop")
