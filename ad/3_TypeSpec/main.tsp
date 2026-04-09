import "@typespec/http";
import "@typespec/openapi3";

using TypeSpec.Http;

@service({
  title: "Library Management API",
})
@server("http://localhost:3000/api", "Library API Server")
namespace LibraryApi {
  model Book {
    id: string;
    title: string;
    authorId: string;
  }

  model BookInput {
    title: string;
    authorId: string;
  }

  @route("/books")
  interface Books {
    @get
    list(): Book[];

    @post
    add(@body book: BookInput): {
      @statusCode code: 201;
    };
  }
}
