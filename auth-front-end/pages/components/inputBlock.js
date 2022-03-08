function InputBlock(props){
    return (
        <div className="h-flex h-ai-flex-center h-jc-space-between inp-block">
            <label htmlFor={props.name}>{props.text}</label>
            <input id={props.id} type={props.type} defaultValue={props.defaultValue}/>
        </div>
    )
}

export default InputBlock