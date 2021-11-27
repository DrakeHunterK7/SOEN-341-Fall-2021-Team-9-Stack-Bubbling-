import React, { Component } from "react";
import Header from "../../components/Header/";
import QuestionBox from "../../components/QuestionBox/";
import AnswerBox from "../../components/AnswerBox";
import axios from "axios"
import "./index.css";

var questiontitle;
var questiontext;
var qUsername;
var qID;
var voteCount;
var newAnswer;

export default class QuestionTemplatePage extends Component {
	constructor(props) {
		super(props);
		this.state = {
		  questiontitle: "",
		  questiontext: "",
		  qUsername:"",
		  qID: "",
		  newAnswer: "",
		  questionVoteCount: 0,
		  AnswersLoaded: false,
		  QuestionLoaded: false,
		  answerList: [],
		};

		this.handleSubmit = this.handleSubmit.bind(this);
    	this.handleChange = this.handleChange.bind(this);
	  }

	  componentDidMount()
	  {
		const { state } = this.props.location;
		this.fetchAnswers();
	  }

	  handleChange(e) {
		this.setState({
		  [e.target.name]: e.target.value,
		});
	  }

	  changeValue(value){
		  this.setState({value});
	  }
	
	  handleSubmit(e) {
		e.preventDefault();
		const { newAnswer} = this.state;
		const { state } = this.props.location;
		qID = state.qID;
		

		const token = localStorage.getItem("access_token");
		
		axios
		  .post("http://localhost:5000/postanswer", {
			question_id: qID,
			body: newAnswer,
		  }, {
			headers: {
			  'Authorization' : 'Bearer ' + token
			}})
		  .then((response) => {
			
			const res = response.status;
			if (res === 200) {
			  
			}
			else if(res === 201){
			  window.location.reload(true);
			}
			else if(res === 204){
			  
			}
		  })
		  .catch(function(error){
			
				if(error.response.status === 500)
				{
				alert('You can only post answers if you are logged in!')
				}
		  })
		  // clean the form
		  this.setState({
			newAnswer:'',
		  });
		  console.log("-----",this.state)
		  
	  }

	  fetchAnswers(){

		const { state } = this.props.location;
		qID = state.qID;
		axios
		.get("http://localhost:5000/listanswers", {
			params: {
				question_id: qID
			}
		})
		.then((response) => {
		  const stat = response.status
		  	if(stat === 201)
		  	{
				this.setState({
			  	answerList: response.data.answerList,
			  	questionVoteCount: response.data.questionVoteCount
				})
				if(this.state.answerList.length > 0)
				{
				this.setState({AnswersLoaded: true})
				}
				this.setState({QuestionLoaded: true})
		  	}	  
		}
		)
		.catch(error => console.log(error))
	  }
	
	
	  
	render() {
		const { state } = this.props.location
		const isQOwner = (localStorage.getItem("username") == state.username)

		const noAnswerStyle = {
			backgroundColor: 'white',
			borderRadius: "5px",
			textDecoration: "none",
			padding:"5px",
			display: "inline-block",
			border: "solid 2px black",
		}
		
		return (
			<div>
				
				<Header />
				{this.state.QuestionLoaded
      			? (
					<QuestionBox onChange={this.handleChange}
					username={state.username} 
					questiontitle = {state.title}
					questiontext= {state.text}
					creationTD={state.creationDateAndTime}
					voteCount={this.state.questionVoteCount}
					questionID = {state.qID}
					/>
            	
      )
      : <p style={noAnswerStyle}>Loading Question.....</p>}
				

				{this.state.AnswersLoaded
      			? (
          			this.state.answerList.map((answer) => <AnswerBox onChange={this.handleChange}
              			username={answer.Username}
              			answertext={answer.body}
						creationDateAndTime={answer.createdAt}
						voteCount={answer.vote_count}
						isBestAnswer={answer.is_best_answer}
						answerID = {answer._id}
						questionID = {state.qID}
						userID = {state.user_id}
						isQuestionOwner={isQOwner}
            	/>)
      )
      : <p style={noAnswerStyle}>No answers posted yet. Be the first to answer!</p>}

				
					
				<div className="post-answer-container">
					<form onSubmit={this.handleSubmit}>
          				<div>
						  <div className="post-answer-title">
                  			<h3>POST ANSWER</h3>
                		</div>
            			<textarea
              			className = "post-answer-textbox" 
              			type="newAnswer"
              			name="newAnswer"
              			value={this.state.newAnswer}
              			onChange={this.handleChange}
        
              			
              			required
            			/>
            
          				</div>
        

          				<div>
            				<button
              				type="submit"
              				className="btn btn-primary btn-lg submit-position post-answer-button"
           				 	>
							Submit
            				</button>
            
          				</div>
					</form>
				</div>
				
				
				
			</div>
			
		)
	}
}