This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app).

## Getting Started

### For Development

First, run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.js`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

### For Production

First, run build the project using following command

```
npm run build
```

Then run the npm

```
npm start
```

The project will start on the declared port on the package.json file.

## About Template

This is a full template for ease start any nextJs project. here included following features, that all are fully customizable for any prject.

* Sample Header and Footer
* Sidebar for Dashboards
* Home page
* Theme toggle (Light/ Dark)
* Role base access control

Please check the Development Instruction section to more info.

## Template SS

![1735533800687](images/README/1735533800687.png)

![1735533818427](images/README/1735533818427.png)

![1735533854502](images/README/1735533854502.png)

## Development Instructions

1. Change the the project running port number in package.json file.

   ```
   "dev": "PORT=4000 next dev",
   ```
2. Make the .env.local file. Rename the example.env.local file into .env.local
3. Basic BE structure of the application

   ![1735533704494](images/README/1735533704494.png)
4. How to update the Header and Sidebar? Simply you can edit the `HeaderMenuItems.js` and `SidebarMenuItems.js` files in the `constant` diretory files.

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.
