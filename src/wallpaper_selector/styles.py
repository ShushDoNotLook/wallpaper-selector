"""CSS styles for the wallpaper selector UI"""

CSS = """
window {
    background-color: #1a1b26;
    border-radius: 12px;
}

.status-bar {
    padding: 8px 20px;
    background-color: #16161e;
    border-top: 1px solid #2f334d;
}

.status-text {
    font-size: 12px;
    color: #565f89;
}

flowbox {
    background-color: transparent;
}

flowboxchild {
    background-color: transparent;
    outline: none;
    padding: 4px;
}

flowboxchild:focus {
    outline: none;
}

flowboxchild:focus .thumbnail {
    outline: 2px solid #7aa2f7;
    outline-offset: 2px;
    border-radius: 8px;
}

.thumbnail {
    background-color: #1f2335;
    border-radius: 8px;
    padding: 8px;
    transition: all 150ms ease;
}

.thumbnail:hover {
    background-color: rgba(122, 162, 247, 0.15);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.preview-image {
    border-radius: 6px;
    background-color: #16161e;
}

.info-box {
    padding: 4px 0;
}

.filename {
    font-size: 11px;
    color: #9aa5ce;
}

.current-badge {
    font-size: 10px;
    color: #7dcfff;
    font-weight: 600;
}

.carousel-image {
    border-radius: 12px;
}

.carousel-label {
    font-size: 14px;
    color: #c0caf5;
}

.carousel-hints {
    font-size: 11px;
    color: #565f89;
}
"""
