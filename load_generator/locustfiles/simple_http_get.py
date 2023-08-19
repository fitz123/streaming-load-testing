from locust import HttpUser, task

class SimpleHttpGetUser(HttpUser):

    @task
    def get_request(self):
        self.client.get("")
