
/**
 * Welcome to Cloudflare Workers!
 *
 * This worker interfaces with the Sandbox container.
 */

export interface Env {
    // If you bound the service/container, it might be available here.
    // For Sandbox, we usually talk to the container service if configured as a service binding
    // or standard HTTP if it's exposing an endpoint.
    // However, usually in 'wrangler dev' with containers, 
    // the Worker and Container run together. 
    // We might need to fetch plain localhost if running locally or use service binding.
}

export default {
    async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
        const url = new URL(request.url);

        // Route to generate telemetry
        if (url.pathname === "/telemetry/generate" && request.method === "POST") {
            // In Cloudflare Sandbox (Workers with Containers), 
            // the container is typically reachable at a specific internal URL or via service binding.
            // For this POC, assuming standard fetch to the container.
            // Note: In beta, this might require specific binding configuration.
            // We'll try fetching localhost port 8000 where our container is listening.

            try {
                // Forward request to the Python container
                // In local dev `wrangler dev`, this often maps to localhost.
                const containerResponse = await fetch("http://localhost:8080/telemetry/generate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: request.body
                });

                return containerResponse;
            } catch (e) {
                return new Response(`Error contacting simulator: ${e}`, { status: 500 });
            }
        }

        return new Response("Sentience Sandbox Worker Active. POST to /telemetry/generate", {
            headers: { "content-type": "text/plain" },
        });
    },
};
