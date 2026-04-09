import "@typespec/http";
import "@typespec/openapi3";

using TypeSpec.Http;

@service({
  title: "Users API",
  version: "1.0.0",
})
@route("/api/users")
namespace UsersApi {
  model User {
    @visibility("read")
    id: int32;

    name: string;
    email: string;
  }

  @get
  @summary("Get all users")
  @operationId("api.get_users")
  op listAll(): User[];

  @post
  @summary("Create a user")
  @operationId("api.create_user")
  op create(@body user: User): { @statusCode code: 201, @body body: User };

  @route("/{userId}")
  @get
  @summary("Get a user by ID")
  @operationId("api.get_user")
  op read(@path userId: int32): User | { @statusCode code: 404, @body error: string };

  @route("/{userId}")
  @put
  @summary("Update a user")
  @operationId("api.update_user")
  op update(@path userId: int32, @body user: User): User | { @statusCode code: 404, @body error: string };

  @route("/{userId}")
  @delete
  @summary("Delete a user")
  @operationId("api.delete_user")
  op delete(@path userId: int32): { @statusCode code: 204 } | { @statusCode code: 404, @body error: string };
}
