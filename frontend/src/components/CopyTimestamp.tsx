export const CopyTimestamp = () => {
  return (
    <div>
      <button
        onClick={() => {
          navigator.clipboard.writeText(String(Date.now()));
        }}
        id="tooltip-default"
        role="tooltip"
        className="absolute z-10 invisible inline-block px-1 py-1 text-sm font-medium text-white transition-opacity duration-300 bg-gray-900 rounded-lg shadow-sm opacity-0 tooltip dark:bg-gray-700"
      >
        <svg
          width="1em"
          height="1em"
          viewBox="0 0 1024 1024"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            fill="#000000"
            d="M512 896a384 384 0 1 0 0-768 384 384 0 0 0 0 768zm0 64a448 448 0 1 1 0-896 448 448 0 0 1 0 896z"
          />
          <path
            fill="#000000"
            d="M480 256a32 32 0 0 1 32 32v256a32 32 0 0 1-64 0V288a32 32 0 0 1 32-32z"
          />
          <path
            fill="#000000"
            d="M480 512h256q32 0 32 32t-32 32H480q-32 0-32-32t32-32z"
          />
        </svg>
        <div className="tooltip-arrow" data-popper-arrow></div>
      </button>
    </div>
  );
};
