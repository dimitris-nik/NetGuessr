import  { useEffect, useState } from 'react'

export default function Website({url}) {
    return (
    <div className="iframe-container">
        {url.length > 0 && <iframe src={url} title="Website" />}
        {url.length === 0 && <p>Loading...</p>}
    </div>)
}