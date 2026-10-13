import grpc
from concurrent import futures
import product_pb2
import product_pb2_grpc


class ProductService(product_pb2_grpc.ProductServicer):
    def GetProduct(self, request, context):
        print("Received request for product ID: {request.id}")
        return product_pb2.ProductResponse(
            id = request.id,
            name = "Super fast Laptop",
            price = 1999.99
        )


def server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers = 10)) # 10 get prod req simultaneously
    product_pb2_grpc.add_ProductServicer_to_server(ProductService(), server)
    # iPv6 networking shortcut: meaning listen to all available n/w interfaces
    # insecure: means we are not using SSL or TLS encryption. Since we are within our own private n/w.
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    server()

