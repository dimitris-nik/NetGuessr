
export default function Website({url}) {
    return (
    <div className="iframe-container">
        {url.length > 0 && <iframe src={url} title="Website" />}
        {url.length === 0 && <div className="loader"></div>}
    </div>)
}