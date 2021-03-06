import React from 'react';
import {useLocation, useHistory} from 'react-router-dom'
import queryString from 'query-string'
import {Box, CircularProgress, Divider, Input, InputAdornment, Typography} from "@material-ui/core";
import {makeStyles} from "@material-ui/core/styles";
import SubdirectoryArrowRightRoundedIcon from '@material-ui/icons/SubdirectoryArrowRightRounded';
import {get_data} from "../ApiCall";
import {URL_POST_SERVICE} from "../Constants";
import PostComponent from "../Component/Post/Post.Component";
import Pagination from "@material-ui/lab/Pagination";
import {HtmlTooltip} from "../Component/Appbar.Component";

const covert_to_search = (text, page) => {
    if (text === '') return
    let array = text.split(':', 2)
    let param = {}
    if (array[0] === 'title') {
        param = {type: 'title', key_word: array[1], page: page}
    } else if (array[0] === 'tags') {
        param = {type: 'tags', key_word: array[1], page: page}
    } else if (array.length === 1) {
        param = {type: 'body', key_word: array[0], page: page}
    } else {
        param = {type: 'body', key_word: array[1], page: page}
    }
    return param
}
const stateLoading = {
    INIT: 0,
    LOADING: 1,
    LOADED: 2
}
const useStyle = makeStyles({
    container: {
        display: 'flex',
        flexDirection: 'row'
    },
    root: {
        padding: '3rem 1rem',
        width: '100%'
    },
    search: {
        fontSize: '2rem',
        border: 'None',
        width: "100%",
        '&:focus': {
            outline: 'None'
        }
    },
    instructorContainer: {}
});
const SearchPage = () => {
    const location = useLocation()
    const history = useHistory()
    const classes = useStyle()
    const page = queryString.parse(location.search).page
    const queryText = queryString.parse(location.search).query
    const [state, setState] = React.useState({
        queryWord: queryText,
        stateLoading: stateLoading.INIT,
        result: {
            posts: [],
            total_pages: 1,
            page: page?page:1,
            itemPerPage: 0,
        }
    })
    const handlePageChange = (e, newVal) => {
        history.push(`/search?query=${queryText}&page=${newVal}`)
    }
    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            //Call API
            document.getElementById('input-with-search').blur()
            let param = covert_to_search(state.queryWord, 0)
            setState({...state, stateLoading: stateLoading.LOADING})
            get_data(URL_POST_SERVICE + '/search', param, false)
                .then(res => {
                    setState({
                        ...state,
                        stateLoading: stateLoading.LOADED,
                        result: {
                            posts: res.data.Post,
                            page: res.data.page,
                            itemPerPage: res.data.itemPerPage,
                            total_pages: res.data.total_pages
                        }
                    })
                })
        }
    }
    const handleChange = (e) => {
        let name = e.target.name
        let val = e.target.value
        setState({
            ...state,
            [name]: val
        })
    }
    React.useEffect(() => {
            let param = covert_to_search(queryString.parse(location.search).query, page?page:1)
            get_data(URL_POST_SERVICE + '/search', param, false)
                .then(res => {
                    setState({
                        ...state,
                        queryWord: queryString.parse(location.search).query,
                        stateLoading: stateLoading.LOADED,
                        result: {
                            posts: res.data.Post,
                            page: res.data.page,
                            itemPerPage: res.data.itemPerPage,
                            total_pages: res.data.total_pages
                        }
                    })
                })
        }
        , [location.search, location.page])
    return (
        <div className={classes.container}>
            <div className={classes.root}>
                <HtmlTooltip disableHoverListener arrow={true} placement="bottom-start"
                             title={
                                 <React.Fragment>
                                     <Typography style={{fontSize: '0.7rem'}}>{`Press `}
                                         <div style={{
                                             border: "1px solid #888a8c",
                                             padding: '0 0.5rem 0 0.5rem',
                                             borderRadius: '3px',
                                             display: 'inline-block'
                                         }}>
                                             <SubdirectoryArrowRightRoundedIcon
                                                 style={{fontSize: '0.7rem', paddingRight: '0.3rem'}}/>
                                             Enter
                                         </div>
                                         {` to search`}</Typography>
                                     <ul className={classes.instructorContainer}>
                                         <li>Type 'keyword' to search on both title and body</li>
                                         <li>Type 'title:keyword' to search on both title</li>
                                     </ul>
                                 </React.Fragment>
                             }
                >
                    <Input className={classes.search} onKeyDown={handleKeyDown}
                           id="input-with-search"
                           onChange={handleChange}
                           name="queryWord" value={state.queryWord}
                           placeholder={'Enter keyword'}
                           startAdornment={(<InputAdornment>
                               <SubdirectoryArrowRightRoundedIcon style={{paddingRight: '1rem', opacity: '0.5'}}/>
                           </InputAdornment>)}
                    />
                </HtmlTooltip>
                <div style={{padding: '2rem 1rem'}}>
                    {
                        state.stateLoading === stateLoading.INIT ? <div></div> :
                            state.stateLoading === stateLoading.LOADING ?
                                <div style={{height: '100vh'}}>
                                    <CircularProgress style={{paddingTop: '3rem'}}/>
                                </div>
                                :
                                <Box style={{textAlign: 'center'}}>
                                    <Box>
                                        {
                                            state.result.posts.map((item, index) => {
                                                return <div key={index}>
                                                    <PostComponent post={item} user={item.author}/>
                                                    <Divider/>
                                                </div>
                                            })
                                        }
                                    </Box>
                                    <Box>
                                        {
                                            state.result.total_pages <= 1 ? null :
                                                <div style={{display: 'flex', flexDirection: 'column', width: '100%'}}>
                                                    <Pagination page={state.result.page} count={state.result.total_pages}
                                                                variant="outlined"
                                                                style={{marginTop: '1rem', alignSelf: 'center'}}
                                                                color="primary" onChange={handlePageChange}/>
                                                </div>
                                        }
                                    </Box>
                                </Box>
                    }
                </div>
            </div>
        </div>
    );
};

export default SearchPage;