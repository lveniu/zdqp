# Project Guidelines

## Code Style
For a Node.js-based coupon grabbing web application, use ESLint for linting and Prettier for code formatting. Follow standard JavaScript conventions: camelCase for variables/functions, PascalCase for classes. Use async/await for asynchronous operations. Example: `const grabCoupon = async (userId, couponId) => { ... }`.

## Architecture
Adopt an MVC (Model-View-Controller) pattern. Models handle data (coupons, users), Views render UI (coupon lists, grab buttons), Controllers manage logic (coupon grabbing, validation). Use Express.js for routing. Data flows: User requests coupon -> Controller validates -> Model updates database -> Response sent. This separates concerns for scalability.

## Build and Test
- Install: `npm install`
- Build: `npm run build` (if using a bundler like Webpack)
- Test: `npm test` (use Jest for unit tests)
- Run: `npm start` (starts the server on port 3000)

## Project Conventions
Use RESTful API endpoints: GET /coupons for listing, POST /coupons/:id/grab for grabbing. Store environment variables in .env file. Log errors with Winston. Avoid global variables; use modules for encapsulation.

## Integration Points
Integrate with e-commerce APIs (e.g., Shopify, WooCommerce) for coupon data. Use Axios for HTTP requests. For payments, integrate Stripe or PayPal SDKs. Communicate via webhooks for real-time updates.

## Security
Validate all inputs with Joi or similar. Use JWT for user authentication. Sanitize database queries to prevent SQL injection. Store secrets in environment variables, not code. Implement rate limiting on grab endpoints to prevent abuse.