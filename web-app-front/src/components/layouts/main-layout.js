function MainLayout({ children }) {
    return (
        <main className="container">
            <div className="row justify-content-center">{children}</div>
        </main>
    );
}

export default MainLayout;
